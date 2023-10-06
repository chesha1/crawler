import os
import signal
import subprocess
import sys
import time
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from fake_useragent import UserAgent

def from_69shuba(id, path):
    # source: https://www.69shuba.com/
    table_of_content_url = 'https://www.69shuba.com/book/{}/'.format(id)
    response = requests.get(table_of_content_url)
    response.raise_for_status()
    response.encoding = 'gbk'
    soup = BeautifulSoup(response.text, 'html.parser')

    # get name of the article
    scripts = soup.find_all('script')
    bookinfo_str = None
    for script in scripts:
        if script.string is None:
            continue
        if 'var bookinfo' in script.string:
            match = re.search(r'var bookinfo = ({.*?});', script.string, re.DOTALL)
            if match:
                bookinfo_str = match.group(1)
                break
    match = re.search(r"articlename\s*:\s*'([^']+)'", bookinfo_str)
    if match:
        article_name = match.group(1)
    print(article_name)

    file_path = '{}{}.txt'.format(path, article_name)
    file = open(file_path, 'w', encoding='utf-8')

    # get table of contents
    url_list = []
    li_tags = soup.find_all('li', attrs={'data-num': True})
    for li in li_tags:
        a_tag = li.find('a')
        if a_tag:
            link = a_tag.get('href')
            if (link != '#'):
                url_list.append(link)

    print('Get {} chapters'.format(len(url_list)))

    for url in tqdm(url_list, desc="Downloading", file=sys.stdout):
        MAX_RETRIES = 5  # 设置最大重试次数
        attempts = 0
        while attempts < MAX_RETRIES:
            try:
                response = requests.get(url)
                break
            except:
                print("An error occurred. Retrying...")
                attempts += 1
            if attempts == MAX_RETRIES:
                print("Max retries reached. Exiting.")
        response.raise_for_status()
        response.encoding = 'gbk'
        soup = BeautifulSoup(response.text, 'html.parser')
        div_tags = soup.find('div', class_='txtnav')
        chapter_content = div_tags.text
        file.write(chapter_content)
        time.sleep(1)

    file.close()


def from_biququ(id, path):
    # source: https://www.biququ.com/
    table_of_content_url = 'https://www.biququ.com/html/{}/'.format(id)

    # get name of the article
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    service = webdriver.ChromeService(executable_path='/opt/homebrew/bin/chromedriver')

    # 启动浏览器
    with webdriver.Chrome(service=service, options=options) as browser:
        browser.get(table_of_content_url)
        all_cookies = browser.get_cookies()
        s = requests.Session()
        for cookie in all_cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        response = s.get(table_of_content_url)

    soup = BeautifulSoup(response.content, 'html.parser')
    meta_tag = soup.find('meta', {'name': 'keywords'})
    if meta_tag:
        content_value = meta_tag.get('content')
        print(content_value)

    print('aaa')


def from_ddxs(name, path):
    # source: https://www.biququ.com/
    table_of_content_url = 'https://www.ddxs.com/{}/'.format(name)

    # get name of the article
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    ua = UserAgent()
    userAgent = ua.chrome
    options.add_argument(f'user-agent={userAgent}')

    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('lang=zh-CN.UTF-8')

    service = webdriver.ChromeService(executable_path='/opt/homebrew/bin/chromedriver')

    headers_in = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Cookie': 'Hm_lvt_120ab3aad23c26d06ff4fefe5da67bc2=1696080216,1696491128; cf_clearance=vZ059LR8Jb8bLVmXLnjlZQrcWaP22ZCkGvhimox5Ov4-1696516030-0-1-232b3f69.ccd626b1.742a6089-0.2.1696516030; __gads=ID=e17704e5ee44ae21-229bce4728e400bc:T=1696080215:RT=1696568240:S=ALNI_MbRO_CUMvaHiXncFE-nZrLysFAbJg; __gpi=UID=00000c559400074a:T=1696080215:RT=1696568240:S=ALNI_MYZQHpvPX6Gro_ZNZjocedTx8QTBQ; Hm_lpvt_120ab3aad23c26d06ff4fefe5da67bc2=1696568240',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'Sec-Fetch-Mode': 'navigate',
        'Referer': 'https://www.ddxs.com/'
    }

    # 启动浏览器
    with webdriver.Chrome(service=service, options=options) as browser:
        browser.get(table_of_content_url)
        all_cookies = browser.get_cookies()
        s = requests.Session()
        for cookie in all_cookies:
            s.cookies.set(cookie['name'], cookie['value'])

        response = s.get(table_of_content_url,headers=headers_in,proxies=proxies)

    soup = BeautifulSoup(response.content, 'html.parser')
    meta_tag = soup.find('meta', {'name': 'keywords'})

    print('aaa')


process = subprocess.Popen([
    "Google Chrome",
    "--remote-debugging-port=19222",
    "--user-data-dir=" + os.path.expanduser('~/ChromeProfile/')
])

proxies = {
    'http': 'socks5h://127.0.0.1:7890',
    'https': 'socks5h://127.0.0.1:7890'
}

path = os.path.expanduser('~/Downloads/')
id = 10043551

from_69shuba(id, path)


os.kill(process.pid, signal.SIGTERM)