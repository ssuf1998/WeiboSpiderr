#!/usr/bin/env python
# encoding: utf-8
"""
@author: ssuf1998
@file: util.py
@time: 2020/6/15 15:50
@desc: Null
"""


def is_blank(str_):
    if str_ and len(str_):
        for c in str_:
            if c not in (' ', '\t', '\n', '\r', '\f', '\v'):
                return False
        return True
    return False
