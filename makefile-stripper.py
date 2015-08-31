#!/usr/bin/env python
import os
import re
import sys
from pprint import pprint

def file_suffix(f):
    t = f.split(".")
    if len(t) == 1:
        return ""
    return t[-1]

def generate_config_dict(name):
    config_dict = {}
    with open(name, "r") as f:
        config_content = f.readlines()
        for config in config_content:
            g = re.match(r'^(?P<config_name>CONFIG(_\w+)+)=(?P<config_val>.+)', config)
            if g is not None:
                config_dict[g.group("config_name")] = g.group("config_val")
    return config_dict

def find_makefile(path):
    makefile_list = []
    c_file_list = []
    for p, d, f in os.walk(path):
        if "Makefile" in f:
            makefile_list.append(os.path.join(p, "Makefile"))
        for t in f:
            if file_suffix(t) in ["h", "c"]:
                c_file_list.append(os.path.join(p, t))
    return makefile_list, c_file_list

def strip_makefile(path, config_dict):
    current_list = []
    with open(path, "r") as f:
        with open("%s.strip" % path, "w") as o:
            makefile_content = f.readlines()
            for line in makefile_content:
                g = re.match(r'^obj-\$\((?P<config_name>CONFIG(_\w+)+)\).*', line)
                if g is not None:
                    if g.group("config_name") in config_dict.keys():
                        current_list.append(line)
                        o.write(line)
                    else:
                        o.write("# %s" % line)
                else:
                    o.write(line)
    return current_list

def expand_macro(path, config_dict):
    f = open(path, "r")
    t = f.readlines()
    f.close()
    f = open(path, "w")
    for l in t:
        g = re.match(r"#ifdef (?P<macro>\w+)", l)
        if g is not None:
            l = "%s # %s\n" % (l.strip(), config_dict.get(g.group("macro")))
        f.write(l)

def main():
    config_dict = generate_config_dict(sys.argv[1])
    makefile_list, c_file_list = find_makefile(os.getcwd())
    f = open("all-objects", "a+")
    for makefile in makefile_list:
        object_list = strip_makefile(makefile, config_dict)
        if len(object_list) != 0:
            f.write(makefile)
            f.write("\n")
            for line in object_list:
                f.write(line)
            f.write("-" * 100)
            f.write("\n")
    f.close()
    for f in c_file_list:
        expand_macro(f, config_dict)
    f = open("%s.strip" % sys.argv[1], "w")
    for key, val in config_dict.items():
        f.write("%s=%s\n" % (key, val))
    f.close()

if __name__ == '__main__':
    main()
