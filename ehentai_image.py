import re

import requests
from requests.exceptions import RequestException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import subprocess
import signal
from tqdm import tqdm
import sys


# def download_gallery_from_image_url_with_num(id, num, id_encry, page, ex=False):
def download_gallery_from_image_url_with_num(initial_url, num, ex, proxy):
    result_url_list = []
    current_url = initial_url
    pbar = tqdm(range(num), desc="Collecting URLs", file=sys.stdout)
    for i in pbar:
        MAX_RETRIES = 5  # 设置最大重试次数
        attempts = 0
        while attempts < MAX_RETRIES:
            try:
                if not ex:
                    if proxy:
                        response = requests.get(current_url, headers=headers, proxies=proxies)
                    else:
                        response = requests.get(current_url, headers=headers)
                else:
                    options = webdriver.ChromeOptions()
                    options.add_argument("--headless")  # 运行浏览器在后台模式
                    options = webdriver.ChromeOptions()
                    options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
                    options.add_argument('--ignore-certificate-errors')
                    options.add_argument('--ignore-ssl-errors')
                    service = webdriver.ChromeService(executable_path='/opt/homebrew/bin/chromedriver')

                    # 启动浏览器
                    with webdriver.Chrome(service=service, options=options) as browser:
                        browser.get(current_url)
                        all_cookies = browser.get_cookies()
                        s = requests.Session()
                        for cookie in all_cookies:
                            s.cookies.set(cookie['name'], cookie['value'])

                        if proxy:
                            response = s.get(current_url, headers=headers, proxies=proxies)
                        else:
                            response = s.get(current_url, headers=headers)
                break
            except RequestException as e:
                print(f"An error occurred: {e}. Retrying...")
                attempts += 1
            if attempts == MAX_RETRIES:
                print("Max retries reached. Exiting.")

        soup = BeautifulSoup(response.content, 'html.parser')
        next_url = soup.find('a', id='next')['href']
        download_link = soup.find('a', string=lambda text: text and 'Download original' in text)
        if download_link is None:
            download_link_small = soup.find('img', id='img')['src']
            download_single_file_using_requests(download_link_small)
        else:
            pbar.set_postfix(current=current_url, refresh=True)
            download_image_from_single_url(download_link['href'])
            result_url_list.append(download_link['href'])

        if next_url == current_url:
            print('Reach final page: {}'.format(next_url))
            break
        else:
            current_url = next_url
            time.sleep(5)

    print("共采集到{}页".format(len(result_url_list)))
    print("-------------------------------------------------")
    # return result_url_list


def download_single_file_using_requests(url):
    if url == 'https://ehgt.org/g/509.gif':
        print("Reach the limit")
        sys.exit()

    MAX_RETRIES = 5  # 设置最大重试次数
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            # avoid ssl error
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
            if proxy:
                response = requests.get(url=url, headers=headers, proxies=proxies)
            else:
                response = requests.get(url=url, headers=headers)
            break
        except RequestException as e:
            print(f"An error occurred: {e}. Retrying...")
            attempts += 1
        if attempts == MAX_RETRIES:
            print("Max retries reached. Exiting.")

    if response.status_code == 200:
        # 从URL中提取文件名
        filename = os.path.basename(url.split(';')[2].split('=')[1])

        # 将内容保存为文件
        with open(os.path.expanduser('~/Downloads/') + filename, "wb") as f:
            f.write(response.content)
    time.sleep(2)


def download_image_from_single_url(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    service = webdriver.ChromeService(executable_path='/opt/homebrew/bin/chromedriver')

    with webdriver.Chrome(service=service, options=options) as browser:
        browser.set_page_load_timeout(30)

        MAX_RETRIES = 5
        attempts = 0
        while attempts < MAX_RETRIES:
            try:
                browser.get(url)
                break
            except TimeoutException:
                print("页面加载超时，正在刷新...")
                attempts += 1
            if attempts == MAX_RETRIES:
                print("Max retries reached. Exiting.")

        current_url = browser.current_url
        time.sleep(2)

        all_cookies = browser.get_cookies()
        s = requests.Session()
        for cookie in all_cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        MAX_RETRIES = 5
        attempts = 0
        while attempts < MAX_RETRIES:
            try:
                requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
                if proxy:
                    response = s.get(current_url, headers=headers, proxies=proxies, timeout=10)
                else:
                    response = s.get(current_url, headers=headers, timeout=20)
                break
            except requests.exceptions.ConnectionError as e:
                print(f"An error occurred: {e}. Retrying...")
                attempts += 1
                browser.refresh()
            if attempts == MAX_RETRIES:
                print("Max retries reached. Exiting.")
        filename = os.path.basename(current_url.split(';')[2].split('=')[1])

        with open(os.path.expanduser('~/Downloads/') + filename, "wb") as f:
            f.write(response.content)


def get_meta_data_from_gallery_url(url, ex, proxy):
    if not ex:
        if proxy:
            response = requests.get(url, headers=headers, proxies=proxies)
        else:
            response = requests.get(url, headers=headers)
    else:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # 运行浏览器在后台模式
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        service = webdriver.ChromeService(executable_path='/opt/homebrew/bin/chromedriver')

        # 启动浏览器
        with webdriver.Chrome(service=service, options=options) as browser:
            browser.get(url)
            all_cookies = browser.get_cookies()
            s = requests.Session()
            for cookie in all_cookies:
                s.cookies.set(cookie['name'], cookie['value'])

            if proxy:
                response = s.get(url, headers=headers, proxies=proxies)
            else:
                response = s.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    # 直接寻找包含'Length:'的td标签
    length_label = soup.find('td', string='Length:')

    if length_label:
        # 找到标签后，获取相邻的兄弟td标签
        length_value_td = length_label.find_next_sibling('td', class_='gdt2')
        if length_value_td:
            # 提取包含页数的文本
            pages_text = length_value_td.text
            # 从这个文本中提取数字
            num_pages = ''.join(filter(str.isdigit, pages_text))
    else:
        raise ValueError("没有找到页码标签")

    gdtm_div = soup.find('div', class_='gdtm')
    a_tag = gdtm_div.find('a')
    first_image = a_tag['href']
    return int(num_pages) + 1, first_image


def get_meta_data_from_image_url(url, ex, proxy):
    pattern = r"(\d+)-(\d+)$"
    match = re.search(pattern, url)
    _, current_page_number = match.groups()

    if not ex:
        if proxy:
            response = requests.get(url, headers=headers, proxies=proxies)
        else:
            response = requests.get(url, headers=headers)
    else:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # 运行浏览器在后台模式
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        service = webdriver.ChromeService(executable_path='/opt/homebrew/bin/chromedriver')

        # 启动浏览器
        with webdriver.Chrome(service=service, options=options) as browser:
            browser.get(url)
            all_cookies = browser.get_cookies()
            s = requests.Session()
            for cookie in all_cookies:
                s.cookies.set(cookie['name'], cookie['value'])

            if proxy:
                response = s.get(url, headers=headers, proxies=proxies)
            else:
                response = s.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    sb_div = soup.find('div', class_='sb')
    a_tag = sb_div.find('a')
    gallery_url = a_tag['href']
    gallery_url = gallery_url.rsplit('/', 1)[0]

    return gallery_url, int(current_page_number)


def download_entire_gallery(url, ex, proxy):
    num_of_pages, first_url = get_meta_data_from_gallery_url(url, ex, proxy)
    download_gallery_from_image_url_with_num(first_url, num_of_pages, ex, proxy)


def download_entire_gallery_from_image_url(url, ex, proxy):
    gallery_url, current_page_number = get_meta_data_from_image_url(url, ex, proxy)
    num_of_pages, _ = get_meta_data_from_gallery_url(gallery_url, ex, proxy)
    download_gallery_from_image_url_with_num(url, num_of_pages - current_page_number + 1, ex, proxy)


def download_from_url(url, ex, proxy):
    # 正则表达式匹配第一种 URL 类型
    ex_string = '-'
    if ex:
        ex_string = 'x'

    pattern1 = r'https://e{}hentai\.org/g/[0-9a-zA-Z]+/[0-9a-zA-Z]+/'.format(ex_string)
    # 正则表达式匹配第二种 URL 类型
    pattern2 = r'https://e{}hentai\.org/s/[0-9a-zA-Z]+/[0-9]+-[0-9]+'.format(ex_string)

    # gallery url
    if re.match(pattern1, url):
        download_entire_gallery(url, ex, proxy)

    # image url
    elif re.match(pattern2, url):
        download_entire_gallery_from_image_url(url, ex, proxy)
    else:
        print("未知的 URL 类型")


process = subprocess.Popen([
    "Google Chrome",
    "--remote-debugging-port=19222",
    "--user-data-dir=" + os.path.expanduser('~/ChromeProfile/')
])

proxies = {
    'http': 'socks5h://127.0.0.1:7890',
    'https': 'socks5h://127.0.0.1:7890'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.'
}

# change parameters here
ex = False
proxy = False
url = 'https://e-hentai.org/s/7b25c310f4/2744786-185'

download_from_url(url, ex, proxy)

os.kill(process.pid, signal.SIGTERM)
