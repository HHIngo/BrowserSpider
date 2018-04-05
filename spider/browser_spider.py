import re
from selenium import webdriver
import json
import os
import time
from selenium.common.exceptions import TimeoutException,NoSuchElementException,StaleElementReferenceException
import codecs
import datetime
from hashlib import md5
from spider.doraemon import scalableBloomFilter, bs, get_xpath
import struct
from spider.alchemy import inferno


# 可选择列表页面的翻页方式，直接地址翻页或点击翻页.可选多次滚动，还是一次滚动,或者不用滚动。
# 可选择不同方式提取，和不同方式输出.提供数据提纯、精炼、转换数据格式等操作，由于需要单独配置，最好调用外部。
# 将非必要导入包安置于doraemon.py中，方便测试。三级以上最好外部调用，都用浏览器效率太低。
class Spider(object):
    # 初始化有点多，但安全
    def __init__(self):
        # 初始化浏览器位置
        self.browser = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
        # 设置浏览器打开页面不超过10s
        self.browser.set_page_load_timeout(10)
        # 提取方式默认为正则
        self.extract_way = "1"
        # 输出数据方式
        self.output_way = "1"
        # 去重方式
        self.dedup_way = "1"
        # 列表页面翻页方式next page way list = next_PWL,默认点击
        self.next_PWL = True
        # 详细页面翻页方式next page way detail next_PWD,默认点击
        self.next_PWD = True
        #  NNP need next page
        self.NNP = False
        # 从模板中提取出的配置字典
        self.load_dict = {}
        # 保存结果字典
        self.result_dict = {}
        # 保存列表页面滚动脚本
        self.list_scroll_script = ""
        # 保存列表页面滚动数值
        self.list_scroll_length = 0
        # 保存详细滚动次数
        self.l_s_time = 0
        # 保存详细页面滚动脚本
        self.details_scroll_script = ""
        # 保存详细页面滚动数值
        self.details_scroll_length = 0
        # 保存详细滚动次数
        self.d_s_time = 0
        # 保存url消息摘要
        self.url_md = ""
        # 保存去重集合
        self.dedup_set = set({})
        # 初始化bloomfilter
        self.bf = scalableBloomFilter()
        # 提纯、精炼、转换数据格式等操作的选择
        self.operate_params = {}

    # 读取模板，读取成字典形式。以名字或id的形式读取。
    def read_template(self, name_or_id):
        file_list = self.get_file_name()
        for name in file_list:
            if name_or_id in name:
                file_name = name
                with open("./template/" + file_name, 'r', encoding='utf-8-sig') as load_f:
                    self.load_dict = json.load(load_f)
                    return
        print("wrong name or id!")

    # 读取路径下的文件名
    def get_file_name(self, file_dir="./template/"):
        file_list = []
        for root, dirs, files in os.walk(file_dir):
            file_list += files
        return file_list

    # 输出数据
    def output_data(self, data):
        if self.output_way == "1":
            self.output_json(data)

    # 输出为本地json文件,output_name由用户输入或者读取配置文件(目前没提供)
    def output_json(self, data, output_name=""):
        if output_name == "":
            filename = codecs.open("./result/"+str(datetime.datetime.now().day)+".json", "a", "utf-8")
        else:
            filename = codecs.open("./result/"+output_name, "a", "utf-8")
        for key, value in data.items():
            if len(value) == 0:
                data[key] = ""
            if len(value) == 1:
                data[key] = data[key][0]
        if not self.operate_params == {}:
            content = self.master_data(data)
        else:
            content = json.dumps(data, ensure_ascii=False)
        filename.write(content + "\n")
        # 输出数据后再记录去重，以免失败后不再进入
        self.write_url_log(self.url_md)

    # 选择提取内容方式
    def do_extract(self, list_or_info_dict, html):
        if self.extract_way == "1":
            self.use_re(list_or_info_dict, html)
        elif self.extract_way == "2":
            self.use_soup()
        elif self.extract_way == "3":
            self.use_xpath()

    # 使用正则,返回所续字段和内容对应字典。
    def use_re(self, list_or_details_dict, html):
        for name, regex in list_or_details_dict.items():
            pattern = re.compile(regex, re.S)
            self.result_dict[name] = pattern.findall(html)

    # 使用BeautifulSoup,模板样式"details":{"taget":{"tagName":{"class" :"dy-num fr"}}},未测试.
    def use_soup(self, list_or_details_dict, html):
        soup = bs(html)
        for name, value in list_or_details_dict.items():
            if type(value) == dict:
                self.result_dict[name] = soup.find_all(list(value.keys())[0],list(value.values())[0])

    # 使用xpath,未测试
    def use_xpath(self, list_or_details_dict, html):
        selector = get_xpath(html)
        for name, path in list_or_details_dict.items():
            self.result_dict[name] = selector.xpath(path).text

    # 去重
    def deduplication(self, href_or_url):
        md = md5()
        md.update(href_or_url.encode("utf8"))
        self.url_md = md.hexdigest()
        # 使用集合去重,在集合内返回真，开始下一次循环
        if self.dedup_way == "1":
            return self.do_deduplication(self.dedup_set)
        # 使用bloomfilter去重
        elif self.dedup_way == "2":
            return self.do_deduplication(self.bf)

    def do_deduplication(self, kind):
        if self.url_md in kind:
            return True
        else:
            return False

    # 可改成一定数量输出和定时输出，以减少io次数，但目前频繁io不太影响性等,打开网页时睡得很足
    def write_url_log(self, url_md):
        if self.dedup_way == "1":
            self.dedup_set.add(url_md)
            log_w = codecs.open("./log/"+self.load_dict["website_id"]+"url_log.log", "w", "utf-8")
            log_w.write(str(self.dedup_set))
        elif self.dedup_way == "2":
            log_w = open("./log/bloomfilter.log", "wb")
            self.bf.add(url_md)
            self.bf.tofile(log_w)
        log_w.close()

    # 首次进入列表页
    def first_blood(self, list_url):
        try:
            self.browser.get(list_url)
        except TimeoutException:
            self.browser.get(list_url)
        if self.next_PWL:
            click_link_id = self.load_dict["click"]["click_link_id"]
            attr_names = list(click_link_id.keys())
            attr_values = list(click_link_id.values())
            self.click_open_list_page(attr_names, attr_values)
            css_next = self.load_dict["click"]["list_next"]
            if not css_next == "":
                try:
                    while True:
                        time.sleep(3)
                        next_list = self.browser.find_element_by_css_selector(css_next)
                        next_list.click()
                        self.click_open_list_page(attr_names, attr_values)
                except NoSuchElementException:
                    print("hey!we can't find it!")
                    return
        else:
            limit = self.load_dict["limit"]
            self.address_open_list_page(list_url, limit)

    # 点击翻页，打开列表页面,详情页也为点击
    def click_open_list_page(self, attr_names, attr_values):
        if not self.list_scroll_script == "":
            self.scroll_page(self.l_s_time, self.list_scroll_length, self.list_scroll_script)
        time.sleep(2)
        links = self.browser.find_elements_by_tag_name("a")
        for link in links:
            try:
                if attr_values[0] in link.get_attribute(attr_names[0]) and attr_values[1] in link.get_attribute(attr_names[1]):
                    href = link.get_attribute("href")
                    if self.deduplication(href):
                        continue
                    link.click()
                    self.click_open_detail_page()
            except TypeError:
                continue
            except StaleElementReferenceException:
                windows = self.browser.window_handles
                if len(windows) > 1:
                    self.browser.close()
                self.browser.switch_to.window(windows[0])
                pass
        links.clear()

    # 拼接翻页，打开列表页面,未测试完
    def address_open_list_page(self, list_url, limit=10):
        list_size = 0
        html = self.browser.page_source
        self.do_extract(self.load_dict["list"], html)
        for link in self.result_dict["link_url"]:
            if self.deduplication(link):
                continue
            full_link = self.load_dict["url_unit"]["url_head"] + link + self.load_dict["url_unit"]["url_foot"]
            print(full_link)
            # url需要拼接，考虑好不同网站的处理方式urlhead + linkurl + urlfoot ...如需要head和foot在模板中配置..
            self.address_open_detail_page(full_link, limit)
        self.result_dict.pop("link_url")
        list_size += self.load_dict["list_size"]
        list_url = list_url + self.load_dict["list_foot"] + str(list_size)
        try:
            self.browser.get(list_url)
        except TimeoutException:
            # 会搞死么。。。
            self.address_open_list_page(list_url)
        self.address_open_list_page(list_url)

    # 点击打开详细页面
    def click_open_detail_page(self):
        windows = self.browser.window_handles
        self.get_data_detail_page(windows)
        # 处理详细页面翻页
        if self.NNP:
            # 用来记录内部页面数量，以防止页面过多，大量垃圾数据
            page_num = 1
            css_next = self.load_dict["click"]["details_next"]
            next_id = self.load_dict["click"]["details_next_id"]
            exit_flag = True
            limit = self.load_dict["limit"]
            while exit_flag and page_num < limit:
                page_num += 1
                links = self.browser.find_elements_by_css_selector(css_next)
                # 判断链接中是否包含下一页等文本
                for next in links:
                    if next.text == next_id:
                        exit_flag = True
                        next.click()
                        self.get_data_detail_page(windows)
                        break
                    else:
                        exit_flag = False
            self.close_or_back(windows)
        else:
            self.close_or_back(windows)

    # 翻页打开详细页面,未测试
    def address_open_detail_page(self, page_url, limit=10):
        windows = self.browser.window_handles
        next_num = self.load_dict["url_unit"]["next_num"]
        toes = next_num
        if self.NNP and self.next_PWD:
            while toes < limit:
                pass
        if len(windows) > 1:
            self.browser.switch_to.window(windows[1])
        page_url = page_url + str(self.load_dict["url_unit"]["next_num"])
        page_url = page_url[:page_url.rfind(str(toes))]
        try:
            self.browser.get(page_url)
        except TimeoutException:
            pass
        toes += next_num
        page_url = page_url + str(next_num)
        self.get_data_detail_page(windows)
        while toes < limit:
            self.address_open_detail_page(page_url)

    # 获取页面数据
    def get_data_detail_page(self, windows):
        if len(windows) > 1:
            self.browser.switch_to.window(windows[1])
        if not self.details_scroll_script == "":
            print("do scroll")
            self.scroll_page(self.d_s_time, self.details_scroll_length, self.details_scroll_script)
        html = self.browser.page_source
        # print(html)
        self.do_extract(self.load_dict["details"], html)
        self.result_dict["url"] = self.browser.current_url
        self.output_data(self.result_dict)

    # 提纯、精炼、转换数据格式等操作,待开发，提纯：如将某一标签(数据)替换换中文或数字等
    def master_data(self, data):
        purify = self.operate_params["purify"]
        refine = self.operate_params["refine"]
        reconstruct = self.operate_params["reconstruct"]
        if purify or refine:
            return inferno(data, purify, refine, reconstruct)

    # 关闭当前窗口或返回
    def close_or_back(self, windows):
        if len(windows) > 1:
            self.browser.close()
            self.browser.switch_to.window(windows[0])
        else:
            self.browser.back()

    # 滚动页面
    def scroll_page(self, s_time, scroll_length, scroll_script):
        time.sleep(2)
        times = s_time
        s_length = 0
        page_len = self.browser.execute_script("return document.body.clientHeight") + scroll_length
        while times > 0 and s_length < page_len:
            s_length += scroll_length
            scroll_js = scroll_script + str(s_length)
            times -= 1
            self.browser.execute_script(scroll_js)
            time.sleep(2)

    # 测试单一详细页面内容是否成功获取, 有些网站直接进入详细页面无法成功加载，还需从列表页进入
    def driect_one_detail_page(self, page_url):
        self.browser.get(page_url)
        html = self.browser.page_source
        self.use_re(self.load_dict["details"], html)
        print(self.result_dict)
        self.output_json(self.result_dict, "test")

    def start_mission(self, name_or_id, list_url, NNP=False, next_PWL=True, next_PWD=True, tortoise={}):
        self.NNP = NNP
        self.next_PWL = next_PWL
        self.next_PWD = next_PWD
        self.read_template(name_or_id)
        self.list_scroll_script = self.load_dict["list_scroll_script"]
        self.list_scroll_length = self.load_dict["list_scroll_length"]
        self.l_s_time = self.load_dict["list_scroll_time"]
        self.details_scroll_script = self.load_dict["details_scroll_script"]
        self.details_scroll_length = self.load_dict["details_scroll_length"]
        self.d_s_time = self.load_dict["details_scroll_time"]
        self.extract_way = self.load_dict["extract_way"]
        self.output_way = self.load_dict["output_way"]
        self.init_dedup()
        if tortoise != {}:
            self.operate_params = tortoise
        self.first_blood(list_url)

    # 初始化去重
    def init_dedup(self):
        self.dedup_way = self.load_dict["dedup_way"]
        if self.dedup_way == "1":
            try:
                file = codecs.open("./log/"+self.load_dict["website_id"]+"url_log.log", "r", "utf-8")
                self.dedup_set = set(re.sub(r"[{}\"\'\s]", "", file.read()).split(","))
                file.close()
            except FileNotFoundError:
                pass
        elif self.dedup_way == "2":
            try:
                file = open("./log/bloomfilter.log", "rb")
                self.bf = self.bf.fromfile(file)
            except struct.error:
                pass
            except FileNotFoundError:
                pass

# 三个重复为提升用户体验，以前输入一般，浏览器开了
if __name__ == "__main__":
    choose = input("fast 1,slow 2,tortoise 3（默认点击翻页，详细页面只打开一页）:")
    input_name_or_id = input("请输入模板名字或id:")
    # list_url = input("列表页面地址:")
    input_list_url = "https://tieba.baidu.com/f?fp=favo&fr=itb_favo&kw=%BA%A3%D4%F4%CD%F5"
    input_next_PWD = True
    tortoise = {}
    if choose == "1":
        spider = Spider()
        spider.start_mission(input_name_or_id, input_list_url)
    elif choose == "2" or choose == "3":
        input_next_PWL = bool(int(input("请输入列表页翻页方式,1点击，0拼接url:")))
        input_NNP = bool(int(input("请输入详细页是否需要翻页,1是，0否:")))
        if input_NNP:
            input_next_PWD = bool(int(input("请输入详细页翻页方式,1点击，0拼接url:")))
        if choose == "2":
            spider = Spider()
            spider.start_mission(input_name_or_id, input_list_url, input_NNP, input_next_PWL, input_next_PWD)
        else:
            tortoise["purify"] = bool(int(input("请输入是否需要(替换特定数据，以便分析),1是，0否:")))
            tortoise["refine"] = bool(int(input("请输入是否需要内容(剔除特定数据),1是，0否:")))
            tortoise["reconstruct"] = bool(int(input("请输入是否需改变数据格式,1是，0否:")))
            spider = Spider()
            spider.start_mission(input_name_or_id, input_list_url, input_NNP, input_next_PWL, input_next_PWD, tortoise)