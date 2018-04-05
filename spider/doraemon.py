from pybloom_live import ScalableBloomFilter
from bs4 import BeautifulSoup
from lxml import etree


# 这几个不用可以加个pass，把return和import注释掉
def scalableBloomFilter():
    return ScalableBloomFilter()


def bs(html):
    return BeautifulSoup(html, "lxml")


def get_xpath(html):
    return etree.HTML(html)

