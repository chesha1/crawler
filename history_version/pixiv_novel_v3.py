import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import json
from selenium import webdriver
import time
import os
import subprocess
import signal


def write_file_line(file, content):
    file.write(content)
    file.write('\n')


def crawler(url, path):
    timestamp = str(int(time.time()))
    # response = requests.get(url)
    # response.raise_for_status()

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
            path_file = path + series_title + " #{} ".format(series_number) + title + '-{}.txt'.format(timestamp)
        else:
            path_file = path + title + '-{}.txt'.format(timestamp)
        with open(path_file, 'w', encoding='utf-8') as file:
            write_file_line(file, timestamp)
            write_file_line(file, novel_stat_str)
            write_file_line(file, novel_content)


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


def get_page_list(url):
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


def get_text_list():
    with open('url_list.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    lines = [line.strip() for line in lines]
    return lines


def crawler_from_text():
    lines = get_text_list()
    for idx, val in enumerate(lines):
        print(f"正在进行第 {idx + 1}/{len(lines)} 个")
        url = val
        crawler(url, path)
        time.sleep(1)


def crawler_from_series(url, url_xhr):
    lines = get_series_list(url_xhr)
    for idx, val in enumerate(lines):
        print(f"正在进行第 {idx + 1}/{len(lines)} 个")
        url = val
        crawler(url, path)
        time.sleep(1)


def crawler_from_page(url_xhr):
    lines = get_page_list(url_xhr)
    for idx, val in enumerate(lines):
        print(f"正在进行第 {idx + 1}/{len(lines)} 个")
        url = val
        crawler(url, path)
        time.sleep(1)


def crawler_from_series_short(id):
    url = "https://www.pixiv.net/novel/series/" + str(id)
    url_xhr = "https://www.pixiv.net/ajax/novel/series_content/" + str(id)
    crawler_from_series(url, url_xhr)


# path should end with '/'
path = ''
# os.system("Google\ Chrome --remote-debugging-port=19222 --user-data-dir='~/ChromeProfile'")
process = subprocess.Popen([
    "Google Chrome",
    "--remote-debugging-port=19222",
    "--user-data-dir=" + os.path.expanduser('~/ChromeProfile')
])

# 4 种类型的爬虫，用其中一种的时候，另外两种都要注释掉
# 1. 直接在 txt 里填好 url 启动就行
# crawler_from_text()

# 2. 系列长度小于 30
id = 1094612
crawler_from_series_short(id)

# 3. url 填系列的地址
# 上面的函数里的 url_xhr 也要改成对应的
# url = "https://www.pixiv.net/novel/series/1413931?p=2"
# url_xhr = "https://www.pixiv.net/ajax/novel/series_content/1413931?limit=30&last_order=30&order_by=asc&lang=zh&version=f32089e9d176912e655d9eda2c1b816e46a82d4b"
# crawler_from_series(url, url_xhr)

# 4. 从一页收藏里爬
# F12 里的项目的名称是 bookmarks?tag=%
# url_xhr = "https://www.pixiv.net/ajax/user/18590339/novels/bookmarks?tag=%E6%9C%AA%E5%88%86%E9%A1%9E&offset=384&limit=24&rest=show&lang=zh&version=f32089e9d176912e655d9eda2c1b816e46a82d4b"
# crawler_from_page(url_xhr)

os.kill(process.pid, signal.SIGTERM)
