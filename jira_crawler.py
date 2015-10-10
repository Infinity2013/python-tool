#!/usr/bin/env python
import re
import sys
import time
import os
from BeautifulSoup import BeautifulSoup
from collections import defaultdict
import openpyxl
from openpyxl.styles import Font, Alignment
import urllib2
from multiprocessing import Pool
search_page_url = [
    'https://jira01.devtools.intel.com/browse/OAM-4695?jql=labels%20%3D%20TopAppsMx%20and%20status%20not%20in%20(closed%2C%20merged%2C%20Implemented)',
    'https://jira01.devtools.intel.com/browse/OAM-3780?jql=labels%20%3D%20Top100Mx%20and%20status%20not%20in%20(closed%2C%20merged%2C%20Implemented)',
]
cookie = "_ga=GA1.2.536659585.1443614850; IntranetSESSION=w+J467+pv3FFa+KaIeXsvPrC0gFCQgNkwAxLULJ6GPadgHBw5sATuhwyENXmRVhqewhCLRM2qUrGSZOLRr2KqGnAq5om/zoyPwQ8/iIr/HSeMyYrXuCemOQDPOYBF0j7MAffGSvFsMiLS/Wq9nXACNv0X+jElQNssUiyInz//Q48yqVDikGa6PgY/Cg+3VNnfuTyWeus9ksB6kilaFAV+12miaqRZZs61QxljW5Fjejaz0l+YeJ6zYxb6ySm6UyL7ygVMD4LunH7v0giJzqXE7i793tHzDoAUtAge2qztBEZINuhbiy8fEg58kIz/lryctNTEXi8JtAcWKyaLaPu++kROWkNKjE4tMnWCvP4TX3aUOnBsAjSurivFM/HDSTu2hhzTearB7UQKMUcXSN1HpizZXrp2turfolYmmytumi6g6m9OosEmYLfkxX0F7yk//JGQNLKyCCLha19K5noyb4htox90115ZOceof1ZUEVAPKXtG56PXmX9jwZ09k2p2RCctMGuvukLjawnVroFzIHJIfiYHpmJxNZUWvRU28FWKZcByTmOsnCa3Spuxz0YgemQV3Hv6rXnD27QNEXxdECL6hESqHDwpQEt3Ky1vi6NUf3t9apEpKrJooQUYS4qlAkm0eGQ8rwLMPwg6YTjwznIT351Sgc8kxjbnfGAjK+P7eebqi7S92A79DQkUAhQghO3vpFlfb8i7khjYxV5elYY73n+h4YtDimUJ3D/PCXj8BcebKEr63JUXdC7b5++8dWDg9z2k1bqZk2AmDZ7tMFSO4hG0YKpwyX08ni5Yn+flqKxar5cWxQBBu9GQuj9SabKz8fPc89lab8o42FtTQ28exkrUMgJziNxq55mNnTe5j+XUdF4HAwnGqc97r0mlkkay/KG04uWW+0JC0yIieuHf8sID8ESYsB2OLYJYJ1OnJ/QdzKGj48G7VEYNb1urymNONuUoiJRBTf9Ybs5BCUtv90EBLWgMOevAbbOt6Ona6pv9TIh/eXLI63RpI1hS2LgiYyqK8aGAOMMBAOyVtHeB+5kBNR6NVrZsz5lDnTJGY4FFIxVpDqdWYhlX4rfWOfxTj1dVG6h9lW9SbhmI6weyWuEWdfz+zlfCjr+uzQnMP86CbPQy28RRGBADx6L; JSESSIONID=6FB3E6AE0EB8AE9EE290EA75D593932A; seraph.rememberme.cookie=128894%3A08c01ba7364948c17f6c4c3b0437d19719c53f7b; atlassian.xsrf.token=BW71-6DCW-73FP-8JMC|38c1456020d2936a3e4144d30c9c5042195ae8f8|lin"

class jira_xml:

    def __init__(self, kargs):
        self.dic = defaultdict()
        for k in kargs:
            self.dic[k] = kargs[k]

    def __getattr__(self, key):
        if key in self.dic:
            return self.dic[key]
        else:
            return None

    def __str__(self):
        s = []
        for k in self.dic.keys():
            val = self.dic[k]
            if type(self.dic[k]) == "set":
                val = " ".join(self.dic[k])
            s.append("%s: %s" % (k, self.dic[k]))
        return "\n".join(s)

class xlsx_position:

    def __init__(self, row, column):
        self.row = str(row)
        self.column = str(column)

    def right(self):
        self.row = chr(ord(self.row) + 1)
        return "%s%s" % (self.row, self.column)

    def left(self):
        self.row = chr(ord(self.row) - 1)
        return "%s%s" % (self.row, self.column)

    def down(self, row):
        self.row = row
        self.column = str(int(self.column) + 1)
        return "%s%s" % (self.row, self.column)

    def cur(self):
        return "%s%s" % (self.row, self.column)

def html_entry_to_unicode(g):
    try:
        return unichr(int(g.group(1)))
    except:
        return g.group(1)

def get_page_source(url):
    headers = {'cookie': '%s' % cookie}
    req = urllib2.Request(url, headers=headers)
    r = urllib2.urlopen(req)
    return re.sub(r'&#(\w+);', html_entry_to_unicode, r.read().decode('utf-8'))


def parse_jira_src(page_src):
    fields = ['summary', 'priority', 'key', 'status', 'project']
    args = defaultdict()
    soup = BeautifulSoup(page_src)
    for f in fields:
        t = soup.find(f).getText()
        args[f] = t

    custom_field_names = soup.findAll('customfieldname')
    for f in custom_field_names:
        if f.getText() == "Bug EXISTS On":
            args['boards'] = set("")
            for value in f.findParent().findAll("customfieldvalue"):
                args['boards'].add(value.getText())
        elif f.getText() == "Platform/Program":
            args['platform'] = set("")
            for value in f.findParent().findAll("customfieldvalue"):
                args['platform'].add(value.getText())
    return jira_xml(args)

def write_to_xlsx(xls, wh, pos, jira_white=None):
    # write link
    font = Font(color='ff0000ff', underline='singleAccounting')
    align = Alignment(vertical='center', wrap_text=True)
    wh[pos.cur()].font = font
    wh[pos.cur()].value = xls.key
    wh[pos.cur()].hyperlink = "https://jira01.devtools.intel.com/browse/%s" % xls.key
    wh[pos.cur()].alignment = align
    wh.row_dimensions[int(pos.column)].height = 30

    # write summay
    wh[pos.right()].value = xls.summary
    wh[pos.cur()].alignment = align
    wh.column_dimensions[pos.row].width = 70
    # write prio
    wh[pos.right()].value = xls.priority
    wh[pos.cur()].alignment = align

    # write platform
    if xls.platform is not None:
        wh[pos.right()].value = " ".join(xls.platform)
        wh[pos.cur()].alignment = align
    else:
        pos.right()

    # write board
    if xls.boards is not None:
        wh[pos.right()].value = " ".join(xls.boards)
        wh[pos.cur()].alignment = align
        wh.column_dimensions[pos.row].width = 70
    else:
        pos.right()

    # write my mark
    if jira_white is not None:
        wh[pos.right()].value = 'checked' if xls.key[6:] in jira_white else 'unchecked'
    else:
        pos.white()

def get_jira_id_list_from_search_page():

    jira_set = set("")
    for url in search_page_url:
        search_src = get_page_source(url)
        g_search = re.findall(r'(GMINL-\d+|OAM-\d+)&quot', search_src)
        if g_search is None:
            raise ValueError("No Jira id in this page.")
        print g_search
        for item in g_search:
            g_jira_id = re.match(r'(?P<id>\w+-\d+)', item)
            if g_jira_id is not None:
                jira_set.add(g_jira_id.group("id"))

    return jira_set

def load_history():
    f = open("%s/jira_black" % sys.path[0], "r")
    jira_black = set(f.readline().split())
    f.close()
    f = open("%s/jira_white" % sys.path[0], "r")
    jira_white = set(f.readline().split())
    f.close()
    return jira_white, jira_black

def update_histroy(f_xlsx):
    wb = openpyxl.load_workbook("%s/%s" % (os.getcwd(), f_xlsx), read_only=True)
    ws = wb.active

    jira_white_old, jira_black_old = load_history()
    jira_white_new, jira_black_new = set(""), set("")
    for row in ws.rows:
        g = re.match(r"GMINL-(?P<id>\d+)", row[0].value)
        if g is not None:
            jira_white_new.add(g.group("id"))
    jira_tmp = set("")
    with open("%s/jira_tmp" % sys.path[0], "r") as f:
        jira_tmp = set(f.readline().split())
    jira_black_new = jira_tmp - jira_white_new
    jira_black_new = jira_black_new | jira_black_old
    jira_white_new = jira_white_new | jira_white_old
    with open("%s/jira_white" % sys.path[0], "w+") as f:
        f.write(" ".join(map(str, jira_white_new)))
    with open("%s/jira_black" % sys.path[0], "w+") as f:
        f.write(" ".join(map(str, jira_black_new)))

def generate_jira_list(jira_set):
    jira_list = []
    for t in jira_set:
        jira_list.append('https://jira01.devtools.intel.com/si/jira.issueviews:issue-xml/%s/%sxml' % (t, t))
    return jira_list

def parse_jira_to_xls(url):
    page_src = get_page_source(url)
    xls = parse_jira_src(page_src)
    print xls
    return xls

def main():
    if len(sys.argv) == 2:
        update_histroy(sys.argv[1])
        return
    wb = openpyxl.workbook.Workbook()
    ws = wb.active
    pos = xlsx_position('A', 1)

    jira_set = get_jira_id_list_from_search_page()
    with open("%s/jira_tmp" % sys.path[0], "w+") as f:
        f.write(" ".join(map(str, jira_set)))
    jira_white, jira_black = load_history()
    jira_avaliable = jira_set - jira_black
    print "Parsed %d jira id" % len(jira_avaliable)
    results = []
    pool = Pool(8)
    try:
        results = pool.map(parse_jira_to_xls, generate_jira_list(jira_set))
    except:
        pool.close()
        pool.join()
    for xls in results:
        write_to_xlsx(xls, ws, pos, jira_white)
        pos.down('A')
    wb.save('test.xlsx')

if __name__ == '__main__':
    main()
