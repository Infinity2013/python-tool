#!/usr/bin/env python
import re
import urllib
from BeautifulSoup import BeautifulSoup
import sys


def generate_page_list(url):
    # http://wenku.baidu.com/view/de25f40a4a7302768e9939dc?pn=1&ssid=&from=&bd_page_type=1&uid=980CD609A635C937C6CE573884994FCC&pu=rc@1,pic@on,sl@1,pw@1000,sz@224_220,pd@1,fz@2,lp@1,tpl@color,&st=1&wk=rd&maxpage=121&pos=last
    g = re.match(r'http://wenku.baidu.com/.*maxpage=(?P<maxpage>\d+).*', url)
    if g is None:
        raise ValueError("invalid url %s" % url)
    maxpage = int(g.group("maxpage"))
    page_list = []
    for i in xrange(1, maxpage + 1):
        t = re.sub(r'pn=\d+', 'pn=%d' % i, url)
        t = t.replace('wenku', 'wapwenku')
        page_list.append(t)


def parse_page(url):
    src = urllib.urlopen(url).read()
    soup = BeautifulSoup(src)
    children = soup.find(attrs={'class': 'ptb45 bgcolor1 xreader'}).findChildren()
    res = []
    for child in children:
        res.append(child.getText())
    return "\n".join(res).encode('utf-8')


def main():
    fd = open("baidu", "w")
    page_list = generate_page_list("http://wenku.baidu.com/view/6660bb14453610661ed9f478?pn=1&ssid=&from=&bd_page_type=1&uid=38DE27B3E71C136688AB60FF2C05C12C&pu=rc@1,pic@on,sl@1,pw@1000,sz@224_220,pd@1,fz@2,lp@1,tpl@color,&st=1&wk=rd&maxpage=132&pos=last")
    for page in page_list:
        fd.write(parse_page(page))

if __name__ == '__main__':
    main()
