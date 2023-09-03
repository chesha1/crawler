import subprocess

from selenium import webdriver
import os

process = subprocess.Popen([
    "Google Chrome",
    "--remote-debugging-port=19222",
    "--user-data-dir=" + os.path.expanduser('~/ChromeProfile/')
])
options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:19222")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

service = webdriver.ChromeService(executable_path='/opt/homebrew/bin/chromedriver')

browser = webdriver.Chrome(service=service, options=options)

browser.get('https://t.bilibili.com/836752529413898288#reply184432979280')
print("aaa")
