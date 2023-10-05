import signal
import subprocess
from selenium import webdriver
import requests
import json
import os
import time


def download(url, file_name):
    try:
        image = requests.get(url=url).content  # 获取图片

    except Exception:
        print(Exception)
        print("网络请求出错！")
    try:
        with open(file_name, 'wb') as f:

            f.write(image)
            f.close()
    except Exception:
        f.close()
        print(Exception)
        print("保存文件过程出错！")


with open("bili.txt", "r") as f:
    id = f.read().splitlines()
# print("-----------------------------------------------------------------------------------------------------")
url_prefix = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id='
url_json_list = [url_prefix + i for i in id]
# print(url_json_list)

process = subprocess.Popen([
    "Google Chrome",
    "--remote-debugging-port=19222",
    "--user-data-dir=" + os.path.expanduser('~/ChromeProfile/')
])

path = os.path.expanduser('~/Library/CloudStorage/OneDrive-123/文件/resources/bili_images/')

for url in url_json_list:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    service = webdriver.ChromeService(executable_path='/opt/homebrew/bin/chromedriver')
    with webdriver.Chrome(service=service, options=options) as browser:
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
        response_json = json.loads(response.content)
        data = json.loads(response_json['data']['card']['card'])
        data_pictures = data['item']['pictures']
        url_list = [i['img_src'] for i in data_pictures]
        for it in url_list:
            strl = it.split("/")
            download(it, path + strl[5])  # 切割了一下，用来保存图片当成文件名，还可以防止图片格式不对
            print(strl[5])
        print(str(url) + " finished.")
        print("-----------------------------------------------------------------------------------------------------")
    time.sleep(3)

with open("bili.txt", "r+") as f:
    f.truncate(0)

os.kill(process.pid, signal.SIGTERM)
