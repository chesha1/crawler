import os

import requests

# 设置socks5代理环境变量
os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:7890'

response = requests.get('https://www.google.com/')

print('aaa')