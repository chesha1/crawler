import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import os
import subprocess
import signal
from tqdm import tqdm
import sys


def get_download_url_list_from_id(id, num, id_encry, page):
    initial_url = 'https://e-hentai.org/s/{}/{}-{}'.format(id_encry, id, page)
    result_url_list = []
    current_url = initial_url
    for i in tqdm(range(num), desc="Collecting URLs", file=sys.stdout):
        response = requests.get(current_url, headers=headers, proxies=proxies)
        soup = BeautifulSoup(response.content, 'html.parser')
        next_url = soup.find('a', id='next')['href']
        if next_url == current_url:
            print('Reach final page: {}'.format(next_url))
            break
        current_url = next_url
        download_link = soup.find('a', string=lambda text: text and 'Download original' in text)
        result_url_list.append(download_link['href'])
        time.sleep(3)

    print("共采集到{}页".format(len(result_url_list)))
    print("-------------------------------------------------")
    return result_url_list


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
id = '2632029'
num = 40
id_encry = '7eb4bedaf7'
page = 481

url_list = get_download_url_list_from_id(id, num, id_encry, page)
download_images_from_list(url_list)

os.kill(process.pid, signal.SIGTERM)