import urllib.request
import re
from selenium import webdriver

def do_static_web(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req)
    return resp.read().decode("utf-8")


def do_real_browser(browser, url):
    #browser = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
    browser.get(url)
    return browser.page_source


def test(html, your_regex):
    #print(html)
    pattern = re.compile(your_regex, re.S)
    content_list = pattern.findall(html)
    print(content_list)

if __name__ == "__main__":
    #your_regex = input("输入要测试的正则:")
    #url = input("输入要测试的url:")
    your_regex = '<div class="threadlist_title pull_left j_th_tit ">.*?href="(.*?)"'
    url = "https://tieba.baidu.com/f?fp=favo&fr=itb_favo&kw=%BA%A3%D4%F4%CD%F5"
    command = input("直接打开输入1，浏览器打开输入2:")
    if command == "1":
        test(do_static_web(url), your_regex)
    elif command == "2":
        browser = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
        test(do_real_browser(browser,url), your_regex)
        browser.close()
    else:
        print("fuck off!")
