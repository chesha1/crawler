import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import subprocess
import signal
from tqdm import tqdm
import sys


def get_download_url_list_from_id(id, num, id_encry, page, ex=False):
    if not ex:
        initial_url = 'https://e-hentai.org/s/{}/{}-{}'.format(id_encry, id, page)
    else:
        initial_url = 'https://exhentai.org/s/{}/{}-{}'.format(id_encry, id, page)
    result_url_list = []
    current_url = initial_url
    for i in tqdm(range(num), desc="Collecting URLs", file=sys.stdout):
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
            result_url_list.append(download_link['href'])

        if next_url == current_url:
            print('Reach final page: {}'.format(next_url))
            break
        else:
            current_url = next_url
            time.sleep(3)

    print("共采集到{}页".format(len(result_url_list)))
    print("-------------------------------------------------")
    return result_url_list


def download_single_file_using_requests(url):
    if url == 'https://ehgt.org/g/509.gif':
        print("Reach the limit")
        sys.exit()
    response = requests.get(url=url, headers=headers, proxies=proxies)
    if response.status_code == 200:
        # 从URL中提取文件名
        filename = os.path.basename(url.split(';')[2].split('=')[1])

        # 将内容保存为文件
        with open(filename, "wb") as f:
            f.write(response.content)


def download_single_file_using_selenium(url):
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

        # 等待下载完成（根据实际情况调整）
        time.sleep(5)  # 假设文件在10秒内下载完成，可能需要调整


def download_images_from_list(url_list):
    if url_list is None:
        return
    for url in tqdm(url_list, desc="Downloading images", file=sys.stdout):
        download_single_file_using_selenium(url)


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
# id: 作品 id
# num: 一共爬取多少页
# page: 从第几页开始
# id_encry: 那一页的链接的 id
# ex: 是否是 exhentai 的作用，不是（默认）就是 False

id = '2683205'
num = 80
id_encry = '0f4e86caab'
page = 1
ex = False

url_list = get_download_url_list_from_id(id, num, id_encry, page, ex)
download_images_from_list(url_list)

os.kill(process.pid, signal.SIGTERM)
