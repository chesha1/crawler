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


# def get_download_url_list_from_id(id, num, id_encry, page, ex=False):
def get_download_url_list_from_id(initial_url, num, ex=False):
    result_url_list = []
    current_url = initial_url
    pbar = tqdm(range(num), desc="Collecting URLs", file=sys.stdout)
    for i in pbar:
        MAX_RETRIES = 5  # 设置最大重试次数
        attempts = 0
        while attempts < MAX_RETRIES:
            try:
                if not ex:
                    response = requests.get(current_url, headers=headers, proxies=proxies)
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

                        response = s.get(current_url, headers=headers, proxies=proxies)
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
    return result_url_list


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

            response = requests.get(url=url, headers=headers, proxies=proxies)
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
                response = s.get(current_url, headers=headers, proxies=proxies, timeout=10)
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


def get_num_of_pages_from_gallery_url(url, ex):
    if not ex:
        response = requests.get(url, headers=headers, proxies=proxies)
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

            response = s.get(url, headers=headers, proxies=proxies)
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
    return int(num_pages) + 1


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
gallery_url = 'https://e-hentai.org/g/2729182/bd5a3e79de/'
initial_url = 'https://e-hentai.org/s/558f4ca23b/2733536-400'
num = 600
ex = False

url_list = get_download_url_list_from_id(initial_url, num, ex)
# num_of_pages = get_num_of_pages_from_gallery_url(gallery_url, ex)

os.kill(process.pid, signal.SIGTERM)
