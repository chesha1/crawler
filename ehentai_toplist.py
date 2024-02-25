import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime


def get_toplist(url, proxy):
    if proxy:
        response = requests.get(url, headers=headers, proxies=proxies)
    else:
        response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    gl3c_divs_1 = soup.find_all('td', class_='gl3c')

    if proxy:
        response = requests.get(url + '&p=1', headers=headers, proxies=proxies)
    else:
        response = requests.get(url + '&p=1', headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    gl3c_divs_2 = soup.find_all('td', class_='gl3c')

    gl3c_divs = gl3c_divs_1 + gl3c_divs_2

    return gl3c_divs


def write_lists_to_file(lists, path):
    """
    将四个列表的内容写入到指定路径的文件中，每个列表的元素占一行，
    不同列表之间空一行。文件名为当前日期。

    :param lists: 包含四个列表的列表
    :param path: 文件将被创建的路径
    """
    # 确保路径存在
    if not os.path.exists(path):
        os.makedirs(path)

    # 创建文件名为今天日期的文件
    today_utc = datetime.utcnow().strftime("%Y-%m-%d")
    file_path = os.path.join(path, f"{today_utc}.txt")

    with open(file_path, 'w') as file:
        for lst in lists:
            for item in lst:
                file.write(f"{item}\n")
            file.write("\n")  # 在不同列表之间添加空行


proxies = {
    'http': 'socks5h://127.0.0.1:7890',
    'https': 'socks5h://127.0.0.1:7890'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.'
}

proxy = True
url1 = 'https://e-hentai.org/toplist.php?tl=11'
url2 = 'https://e-hentai.org/toplist.php?tl=12'
url3 = 'https://e-hentai.org/toplist.php?tl=13'
url4 = 'https://e-hentai.org/toplist.php?tl=15'

result_list = list()
result_list.append(get_toplist(url1, proxy))
result_list.append(get_toplist(url2, proxy))
result_list.append(get_toplist(url3, proxy))
result_list.append(get_toplist(url4, proxy))

path = os.path.expanduser('~/Desktop/ehgt')
write_lists_to_file(result_list, path)
