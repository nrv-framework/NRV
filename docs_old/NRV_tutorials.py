#! /usr/bin/env python3
# coding: utf-8
import argparse
import os
import re
from pathlib import Path

#tutorial_folders = ["./generic/","./optim/"]


## ARGUMENT PARSER ##
parser = argparse.ArgumentParser(description="NeuRon Virtualizer automated tutorial module")
parser.add_argument("-a", "--all", dest="ALL_TUTO", help="Lauch all tutorial",action="store_true")
parser.add_argument("-t", "--target", dest="TARGET_TUTO", type=str, nargs="+" ,default='0', help="ID of the example to run")


def get_ipybn_path ():
    filenames = sorted(os.listdir())
    return [filename for filename in filenames if filename.endswith(".ipynb")]

def get_targeted_example(TARGET_EXAMPLE):
    if TARGET_EXAMPLE != '0':
        N = len(TARGET_EXAMPLE)
        offset = 0
        for i in range(N):
            argt = TARGET_EXAMPLE[i+offset]
            if "_" in argt:
                arg_offset = 1
                new_argt = [argt]
                if argt[-1] == "_":
                    new_argt = [argt[:-1]+str(i) for i in range(10)]
                    arg_offset *= 10
                if len(new_argt[0]) > 2:
                    if new_argt[0][-2] == "_":
                        old_argt = new_argt
                        new_argt = []
                        for arg in old_argt:
                            new_argt += [arg[:-2]+str(i)+arg[-1] for i in range(10)]
                        arg_offset *= 10
                if len(new_argt[0]) > 3:
                    if new_argt[0][-3] == "_":
                        old_argt = new_argt
                        new_argt = []
                        for arg in old_argt:
                            new_argt += [arg[:-3]+str(i)+arg[-2:] for i in range(10)]
                        arg_offset *= 10
                TARGET_EXAMPLE = TARGET_EXAMPLE[:i+offset] + new_argt + TARGET_EXAMPLE[i+offset+1:]
                offset += arg_offset
        TARGET_EXAMPLE.sort()
        return(TARGET_EXAMPLE)

def filter_example(path_l, filter_l):
    dig_l = set([list(map(int, re.findall(r'\d+', p)))[0] for p in path_l])
    filter_l = set([int(f) for f in filter_l])
    targeted_idx = list(dig_l & filter_l)
    examples = [path for path in path_l if list(map(int, re.findall(r'\d+', path)))[0] in targeted_idx]
    return(examples)


if __name__ == "__main__":

    args = parser.parse_args()
    path_l = []
    if args.ALL_TUTO: 
        path_l=get_ipybn_path()

    if args.TARGET_TUTO != '0':
        filter_ex = get_targeted_example(args.TARGET_TUTO)
        path_l=get_ipybn_path()
        path_l = filter_example(path_l,filter_ex)    

    print(f"Targeted Tutorial(s): {path_l}")

    for ex in path_l:
        print(ex)
        os.system(f'ipython -c "%run {ex}"')


    

