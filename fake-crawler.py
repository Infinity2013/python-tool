#!/usr/bin/env python
import re
import sys
import os
import clipboard
import time


def parse_jira_id_from_file(f_name):
    with open(f_name, "r") as f:
        g = re.findall(r"GMINL-\d+&quot", f.readline())
        if g is not None:
            return g
        else:
            print "Wrong"
            sys.exit()

def unique_jira_id_and_sort(l_id):
    s_id = set("")
    for item in l_id:
        g = re.match(r"GMINL-(?P<id>\d+)&quot", item)
        if g is not None:
            s_id.add(int(g.group("id")))
    return s_id

def load_histroy():
    with open("jira_history", "r+") as f:
        return set(map(int, f.readline().split()))

def save_history(s_history):
    with open("jira_history", "w+") as f:
        f.write(" ".join(map(str, s_history)))

def savexml():
    os.system("xdotool mousemove 28 294")
    os.system("xdotool click 1")
    os.system("xdotool key F6")
    os.system("xdotool key ctrl+v")
    os.system("xdotool key Return")

    time.sleep(5)
    os.system("xdotool key ctrl+s")
    time.sleep(1)
    os.system("xdotool key Return")
    time.sleep(0.5)

def prepare():
    os.system("xdotool mousemove 28 294")
    os.system("xdotool click 1")
    time.sleep(0.5)

    os.system("xdotool mousemove 237 41")
    os.system("xdotool click 1")
    time.sleep(0.5)

    os.system("xdotool mousemove 28 294")
    os.system("xdotool click 1")
    time.sleep(0.5)

def main():
    l_id = parse_jira_id_from_file(sys.argv[1])
    s_id = unique_jira_id_and_sort(l_id)
    s_id_histroy = load_histroy()
    s_id_not_recorded = s_id - s_id_histroy
    prepare()
    for item in s_id_not_recorded:
        addr = "https://jira01.devtools.intel.com/si/jira.issueviews:issue-xml/GMINL-%d/GMINL-%dxml" % (item, item)
        clipboard.copy(addr)
        savexml()
        s_id_histroy.add(item)
        save_history(s_id_histroy)

if __name__ == '__main__':
    main()
