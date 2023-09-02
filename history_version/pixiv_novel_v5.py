import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import json
from selenium import webdriver
import time
import math
import os
import subprocess
import signal
import re
from datetime import datetime, timedelta


def write_file_line(file, content):
    file.write(content)
    file.write('\n')


def clean_filename(filename):
    # 此正则表达式将找到Windows中的非法字符
    # 如果你在其他操作系统上，你可能需要修改这个正则表达式
    pattern = r'[<>:"/\\|?*]'
    return re.sub(pattern, "_", filename)  # 将非法字符替换为下划线


def crawler(url, path):
    timestamp = str(int(time.time()))

    try:
        response = requests.get(url)
        response.raise_for_status()
        # 如果HTTP请求是成功的，接下来的代码会执行

    except HTTPError as http_err:
        if response.status_code == 404:
            print('Error 404: Not Found. 可能是访问了好P友限定作品')
            return

        else:
            print(f'An HTTP error occurred: {http_err}')  # 其他的HTTP错误
    except Exception as err:
        print(f'An error occurred: {err}')  # 其他错误

    soup = BeautifulSoup(response.text, 'html.parser')

    meta_tag = soup.find('meta', attrs={"name": "preload-data"})
    meta_content = meta_tag['content']
    meta_content = json.loads(meta_content)
    pid = list(meta_content['novel'].keys())[0]
    novel_stat = meta_content['novel'][pid]
    title = novel_stat['title']
    if novel_stat['seriesNavData'] == None:
        in_series = False
    else:
        in_series = True
        series_title = novel_stat['seriesNavData']['title']
        series_number = novel_stat['seriesNavData']['order']
    novel_stat_str = json.dumps(novel_stat, ensure_ascii=False)

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
    # 使用 Chrome 驱动
    with webdriver.Chrome(options=options) as browser:
        browser.get(url)

        # 获取所有的cookies
        all_cookies = browser.get_cookies()

        # 使用 requests 与 cookies
        s = requests.Session()

        for cookie in all_cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.'
        }
        response = s.get(url, headers=headers)

        soup = BeautifulSoup(response.content, 'html.parser')
        meta_tag = soup.find('meta', attrs={'name': 'preload-data'})
        meta_content = meta_tag['content']
        meta_content = json.loads(meta_content)
        pid = list(meta_content['novel'].keys())[0]
        novel_stat = meta_content['novel'][pid]

        novel_content = novel_stat['content']

        if in_series == True:
            path_file = path + clean_filename(series_title) + " #{} ".format(series_number) + clean_filename(
                title) + '-{}.txt'.format(timestamp)
        else:
            path_file = path + clean_filename(title) + '-{}.txt'.format(timestamp)
        with open(path_file, 'w', encoding='utf-8') as file:
            write_file_line(file, timestamp)
            write_file_line(file, novel_stat_str)
            write_file_line(file, novel_content)
    time.sleep(4)


def get_xhr_list_from_series_id(id):
    series_intro_url = "https://www.pixiv.net/ajax/novel/series/{}".format(id)
    response = requests.get(series_intro_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser').text
    soup_content = json.loads(soup)
    num_novel = soup_content['body']['publishedContentCount']
    num_page = math.ceil(num_novel / 30)
    xhr_list = []
    for i in range(num_page):
        url_temp = "https://www.pixiv.net/ajax/novel/series_content/{}?limit=30&last_order={}".format(id, 30 * i)
        xhr_list.append(url_temp)
    return xhr_list


def get_series_list(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser').text
    soup_content = json.loads(soup)
    url_dict = soup_content['body']['page']['seriesContents']
    url_list = []
    for i in url_dict:
        url_list.append('https://www.pixiv.net/novel/show.php?id=' + i['id'])
    return url_list


def get_url_list_from_page_xhr(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
    # 使用 Chrome 驱动
    with webdriver.Chrome(options=options) as browser:
        browser.get(url)

        # 获取所有的cookies
        all_cookies = browser.get_cookies()

        # 使用 requests 与 cookies
        s = requests.Session()

        for cookie in all_cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.'
        }
        response = s.get(url, headers=headers)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser').text
        soup_content = json.loads(soup)
        url_dict = soup_content['body']['works']
        url_list = []
        for i in url_dict:
            url_list.append('https://www.pixiv.net/novel/show.php?id=' + i['id'])
        return url_list


def get_url_list_from_url_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    lines = [line.strip() for line in lines]
    return lines


def get_id_list_from_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    lines = [int(line.strip()) for line in lines]
    return lines


def crawler_from_url_file(save_path, file_path):
    url_list = get_url_list_from_url_file(file_path)
    for idx, val in enumerate(url_list):
        print(f"正在进行第 {idx + 1}/{len(url_list)} 个")
        crawler(val, save_path)
    with open(file_path, "r+") as f:
        f.truncate(0)


def crawler_from_id_file(path, id_path):
    id_list = get_id_list_from_file(id_path)
    for idx, id in enumerate(id_list):
        print("-------------------------------------")
        print(f"正在进行第 {idx + 1}/{len(id_list)} 组任务")
        crawler_from_series_id(path, id)
    with open(id_path, "r+") as f:
        f.truncate(0)


def get_url_list_from_xhr_list(xhr_list):
    total_list = []
    for url_xhr in xhr_list:
        lines = get_series_list(url_xhr)
        total_list[0:0] = lines
    total_list = sorted(list(set(total_list)))
    return total_list


def crawler_from_xhr_list(path, xhr_list):
    url_list = get_url_list_from_xhr_list(xhr_list)
    for idx, val in enumerate(url_list):
        print(f"正在进行第 {idx + 1}/{len(url_list)} 个")
        crawler(val, path)


def crawler_single_from_page_xhr(path, url_xhr):
    url_list = get_url_list_from_page_xhr(url_xhr)
    for idx, val in enumerate(url_list):
        print(f"正在进行第 {idx + 1}/{len(url_list)} 个")
        crawler(val, path)


def crawler_from_series_id(path, id):
    xhr_list = get_xhr_list_from_series_id(id)
    crawler_from_xhr_list(path, xhr_list)


def crawler_complex_from_page_xhr(path, url_xhr):
    url_list = get_url_list_from_page_xhr(url_xhr)
    url_single_list = []
    id_list = []
    for url in url_list:
        try:
            response = requests.get(url)
            response.raise_for_status()
            # 如果HTTP请求是成功的，接下来的代码会执行

        except HTTPError as http_err:
            if response.status_code == 404:
                print('Error 404: Not Found. 可能是访问了好P友限定作品')
                return

            else:
                print(f'An HTTP error occurred: {http_err}')  # 其他的HTTP错误
        except Exception as err:
            print(f'An error occurred: {err}')  # 其他错误

        soup = BeautifulSoup(response.text, 'html.parser')

        meta_tag = soup.find('meta', attrs={"name": "preload-data"})
        meta_content = meta_tag['content']
        meta_content = json.loads(meta_content)
        pid = list(meta_content['novel'].keys())[0]
        novel_stat = meta_content['novel'][pid]
        if novel_stat['seriesNavData'] == None:
            url_single_list.append(url)
        else:
            series_id = novel_stat['seriesNavData']['seriesId']
            id_list.append(series_id)

    for idx, val in enumerate(url_single_list):
        print(f"正在进行第 {idx + 1}/{len(url_list)} 个")
        crawler(val, path)
    for idx, id in enumerate(id_list):
        print("-------------------------------------")
        print(f"正在进行第 {idx + 1}/{len(id_list)} 组任务")
        crawler_from_series_id(path, id)


def generate_date_list(start_date, end_date):
    # 将给定的日期字符串转换为datetime对象
    start_dt = datetime.strptime(start_date, '%Y%m%d')
    end_dt = datetime.strptime(end_date, '%Y%m%d')

    current_dt = start_dt
    dates = []

    # 循环生成日期列表
    while current_dt <= end_dt:
        dates.append(current_dt.strftime('%Y%m%d'))
        current_dt += timedelta(days=1)

    return dates


def crawler_single_from_day_toplist(path, start_date, end_date):
    date_list = generate_date_list(str(start_date), str(end_date))
    page_url_list = ['https://www.pixiv.net/novel/ranking.php?mode=daily_r18&date=' + i for i in date_list]
    url_list = []

    # 把这一个日期，也就是这一页的所有 url 收集起来，是中文的就添加到 url_list 列表中
    for idx, page_url in enumerate(page_url_list):
        if idx % 10 == 0:
            print("已完成{}/{}页的 url 采集".format(idx + 1, len(page_url_list)))
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
        # 使用 Chrome 驱动
        with webdriver.Chrome(options=options) as browser:
            browser.get(page_url)

            # 获取所有的cookies
            all_cookies = browser.get_cookies()

            # 使用 requests 与 cookies
            s = requests.Session()

            for cookie in all_cookies:
                s.cookies.set(cookie['name'], cookie['value'])

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.'
            }
            response = s.get(page_url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            pattern = re.compile(r'/novel/show\.php\?id=\d+')

            links = soup.find_all('a', href=pattern)
            link_list = list(set([link['href'] for link in links]))
            for link in link_list:
                try:
                    response_link = requests.get('https://www.pixiv.net' + link, headers=headers)
                    response_link.raise_for_status()
                    # 如果HTTP请求是成功的，接下来的代码会执行

                except HTTPError as http_err:
                    if response.status_code == 404:
                        return

                    else:
                        print(f'An HTTP error occurred: {http_err}')  # 其他的HTTP错误
                except Exception as err:
                    print(f'An error occurred: {err}')  # 其他错误

                soup_link = BeautifulSoup(response_link.text, 'html.parser')

                meta_tag = soup_link.find('meta', attrs={"name": "preload-data"})
                meta_content = meta_tag['content']
                meta_content = json.loads(meta_content)
                pid = list(meta_content['novel'].keys())[0]
                novel_stat = meta_content['novel'][pid]
                novel_lang = novel_stat['language']
                if novel_lang == 'zh-cn':
                    url_list.append('https://www.pixiv.net' + link)

    url_list = list(set(url_list))
    url_length = len(url_list)
    print("共采集到{}篇小说".format(url_length))
    print("-------------------------------------------------")
    for idx, url in enumerate(url_list):
        if idx % 10 == 0:
            print(f"正在进行第 {idx + 1}/{url_length} 个")
        crawler(url, path)


# path should end with '/'
# path = ''
path = ''
single_url_file_path = ''
id_file_path = ''
series_id = 9323428
url_xhr = ""
start_date = 20230501
end_date = 20230531

# os.system("Google\ Chrome --remote-debugging-port=19222 --user-data-dir='~/ChromeProfile'")
process = subprocess.Popen([
    "Google Chrome",
    "--remote-debugging-port=19222",
    "--user-data-dir=" + os.path.expanduser('~/ChromeProfile')
])

# 5 种类型的爬虫，用其中一种的时候，另外两种都要注释掉

# 1. 来源是 txt 文件里的 url，从 url 爬取单篇小说
# crawler_from_url_file(path, single_url_file_path)

# 2. 来源是系列 id，从系列 id 爬取一整个系列的小说
# crawler_from_series_id(path, series_id)

# 3. 来源是 txt 文件里的系列 id
# crawler_from_id_file(path, id_file_path)

# 4. 从一页收藏里爬，获取这一页中每篇小说
# F12 里的项目的名称是 bookmarks?tag=%
# crawler_single_from_page_xhr(path, url_xhr)

# 5. 从一页收藏里爬，获取这一页中每篇小说，如果这篇小说存在系列，获取所属系列的所有小说
# F12 里的项目的名称是 bookmarks?tag=%
# crawler_complex_from_page_xhr(path,url_xhr)

# 6. 从一页 toplist 里获取这一页的所有中文小说，不溯源所在的系列
crawler_single_from_day_toplist(path, start_date, end_date)

os.kill(process.pid, signal.SIGTERM)
