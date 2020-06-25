#!/usr/bin/env python
# encoding: utf-8
"""
@author: ssuf1998
@file: util.py
@time: 2020/6/15 15:50
@desc: Null
"""
import csv
import datetime
import json
import re
import time


def is_blank(str_):
    if str_ and len(str_):
        for c in str_:
            if c not in (' ', '\t', '\n', '\r', '\f', '\v'):
                return False
        return True
    return False


def get_abs_time(time_str):
    if '今天' in time_str:
        return time_str.replace(
            '今天', time.strftime('%#m{m}%#d{d}',
                                time.localtime(time.time())).format(m='月', d='日'))
    elif '分钟前' in time_str:
        delta_minute = datetime.timedelta(minutes=int(time_str.replace('分钟前', '')))
        now_time = datetime.datetime.now()
        return (now_time - delta_minute).strftime('%#m{m}%#d{d} %H:%M').format(m='月', d='日')
    else:
        return time_str


def flat_multimedia(elements):
    for element in elements:
        if element.name == 'img':
            element.replace_with(element.get('alt'))
        elif element.name == 'a':
            if element.get('extra-data') in ('type=atname', 'type=topic'):
                element.replace_with(element.text)
            else:
                element.replace_with('')


def clean_content(wrap, prefix='>：', suffix='<'):
    content_ = wrap.select_one('div.WB_text')

    flat_multimedia(wrap.select('div .WB_text > img'))
    flat_multimedia(wrap.select('div .WB_text > a'))

    content_temp = re.search(r'(?<={prefix})(.*?)(?={suffix})'.format(prefix=prefix, suffix=suffix),
                             str(content_).replace('\n', ''))
    if content_temp:
        content_ = content_temp.group().strip()

        if is_blank(content_):
            content_ = ''
    else:
        content_ = ''

    return content_


def get_arg(get_str, arg_name):
    result = re.search(r'(?<=&{arg_name}=)(.*?)(?=&)'.format(arg_name=arg_name), get_str)
    if result:
        return result.group()


def multi_format_output(save_format, file_name, header_row, dict_data):
    if save_format == 'no':
        print(json.dumps(dict_data, ensure_ascii=False))
    elif save_format in ('json', 'txt'):
        with open('{}.{}'.format(file_name, save_format),
                  mode='w',
                  encoding="utf-8") as fp:
            json.dump(dict_data, fp, ensure_ascii=False)
    else:
        with open('{}.csv'.format(file_name),
                  mode='w',
                  encoding="utf-8-sig",
                  newline='') as fp:
            csv_writer = csv.writer(fp)
            csv_writer.writerow(header_row)
            for key, value in dict_data.items():
                row = ['|'.join(v) if isinstance(v, list) else v for v in value.values()]
                row.insert(0, key)
                csv_writer.writerow(row)


if __name__ == '__main__':
    pass
