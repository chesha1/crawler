import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
import time
import re
from urllib.parse import urlparse


# use the following command to open chrome
# Google\ Chrome --remote-debugging-port=19222 --user-data-dir="~/ChromeProfile"

def remove_hash_prefix_except_numbers(s):
    def replace(match):
        # 如果片段是#数字则返回原片段，否则返回空字符串
        return match.group() if match.group().lstrip('#').isdigit() else ''

    # 找到所有#开头的片段，然后基于replace函数进行替换
    return re.sub(r'#\w+', replace, s).lstrip()


def remove_pixiv_suffix(s):
    suffix = " - pixiv"
    if s.endswith(suffix):
        return s[:-len(suffix)]
    return s


def reformat(s):
    s = re.sub(r'^\[[^]]+\]\s*', '', s)  # remove prefix
    s = remove_hash_prefix_except_numbers(s)
    s = remove_pixiv_suffix(s)
    s = s.split('|', 1)[0].strip()  # remove pipe and after
    s = s.split('-', 1)[0].strip()  # remove dash and after
    return s


def write_file_line(file, content):
    file.write(content)
    file.write('\n')


def crawler(url):
    timestamp = str(int(time.time()))
    response = requests.get(url)
    response.raise_for_status()  # 确保响应状态码为 200

    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, 'html.parser')
    # title = reformat(soup.title.string)

    meta_tag = soup.find('meta', attrs={"name": "preload-data"})
    meta_content = meta_tag['content']
    meta_content = json.loads(meta_content)
    pid = list(meta_content['novel'].keys())[0]
    novel_stat = meta_content['novel'][pid]
    title = novel_stat['title']
    if novel_stat['seriesNavData']==None:
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

        path = '~/Library/CloudStorage/OneDrive-123/文件/resources/p小说/'
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
    response.raise_for_status()  # 确保响应状态码为 200

    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, 'html.parser').text
    soup_content = json.loads(soup)
    url_dict = soup_content['body']['page']['seriesContents']
    url_list = []
    for i in url_dict:
        url_list.append('https://www.pixiv.net/novel/show.php?id=' + i['id'])
    return url_list


def get_series_prefix(url):
    response = requests.get(url)
    response.raise_for_status()  # 确保响应状态码为 200

    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string
    title = title.split('/', 1)[0].strip()
    title = title[1:-1]
    return title


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
        crawler(url)
        time.sleep(5)


def get_last_segment(url):
    path = urlparse(url).path
    return path.split('/')[-1]


def crawler_from_series(url, url_xhr):
    title_prefix = get_series_prefix(url) + " "
    id = get_last_segment(url)
    lines = get_series_list(url_xhr)
    for idx, val in enumerate(lines):
        print(f"正在进行第 {idx + 1}/{len(lines)} 个")
        url = val
        crawler(url)
        time.sleep(5)


# 直接在 txt 里填好 url 启动就行
crawler_from_text()

# url 填系列的地址
# 上面的函数里的 url_xhr 也要改成对应的
# url = "https://www.pixiv.net/novel/series/"
# url_xhr = "https://www.pixiv.net/ajax/novel/series_content/"
# crawler_from_series(url, url_xhr)
