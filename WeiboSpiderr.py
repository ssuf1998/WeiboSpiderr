#!/usr/bin/env python
# encoding: utf-8
"""
@author: ssuf1998
@file: WeiboSpiderr.py
@time: 2020/6/15 14:29
@desc: Null
"""

import re
import json
import time
import csv

import requests
from bs4 import BeautifulSoup

from util import is_blank


class WeiboSpiderr(object):
    def __init__(self, weibo_url, cookie, page_range=(1, 1)) -> None:
        self.__WEIBO_DETAIL_URL = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&id={mid}&page={page}&filter=hot&from=singleWeiBo&__rnd={timestamp}'
        self.__WEIBO_LIST_URL = '{weibo_url}?page={page}'
        self.__UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
        self.__headers = {
            'user-agent': self.__UA,
            'cookie': ''
        }

        self.cookie = cookie
        self.page_range = page_range
        self.weibo_url = weibo_url

        self.__weibos = []
        self.__comments = {}

    def __get_weibos(self):
        for i in range(self.page_range[0], self.page_range[1] + 1):
            mids = []
            request = requests.get(
                url=self.__WEIBO_LIST_URL.format(weibo_url=self.weibo_url, page=i),
                headers=self.__headers)
            request.encoding = 'utf-8'
            bs = BeautifulSoup(request.text, 'lxml')

            for script in bs.select('script'):
                json_str = re.search(r'(?<=FM.view\()(.*)(?=\))', str(script))
                if json_str:
                    json_obj = json.loads(json_str.group())
                    if 'Pl_Official_MyProfileFeed' in json_obj['domid']:
                        bs = BeautifulSoup(json_obj['html'], 'lxml')
                        break

            weibos = bs.select('div[mid]')

            for weibo in weibos:
                mids.append(weibo.get('mid'))

            self.__weibos.append(mids)
            time.sleep(0.2)

    def __get_comment_info(self, mid):
        self.__comments = {}
        page = 1
        # 进循环尽可能多的获取评论
        while True:
            last_len = len(self.__comments)
            request = requests.get(
                url=self.__WEIBO_DETAIL_URL.format(
                    mid=mid,
                    page=page,
                    timestamp=int(round(time.time() * 1000))),
                headers=self.__headers)
            request.encoding = 'utf-8'

            bs = BeautifulSoup(request.json()['data']['html'], 'lxml')

            # 逐条评论爬取
            for wrap in bs.select('div[node-type="root_comment"]'):
                # 评论uuid，用作键值
                comment_id = wrap.get('comment_id')

                # 评论人用户名
                user_name = wrap.select_one('a[usercard]').getText()
                # 评论人微博主页链接
                user_url = 'https:' + wrap.select_one('a[usercard]').get('href')
                # 评论内容
                content = wrap.select_one('div.WB_text')
                # 评论内容中的表情清洗成字符串方便存储
                content_imgs = wrap.select('div .WB_text > img')
                if content_imgs:
                    for img in content_imgs:
                        img.replace_with(img.get('alt'))

                # 评论内容中的超链接（@某人的情况）清洗成字符串
                content_as = wrap.select('div .WB_text > a')
                if content_as:
                    for a in content_as:
                        a.replace_with(a.text if a.text != '¡评论配图' else '')

                # 正则表达式拿到干净的评论内容
                content_temp = re.search(r'(?<={}：)(.*?)(?=<)'.format(user_name),
                                         str(content).replace('\n', ''))
                if content_temp:
                    content = content_temp.group().strip()
                    if is_blank(content):
                        content = ''
                else:
                    content = ''
                # 评论时间格式化，将“今天”转化为日期
                comment_time = wrap.select_one('div .WB_from.S_txt2').getText().replace(
                    '今天', time.strftime('%#m{m}%#d{d}',
                                        time.localtime(time.time())).format(m='月', d='日'))
                # 处理评论中的插入图片
                media_pics = wrap.select('div .WB_media_wrap .WB_pic img')
                media_urls = []
                # 插入图片获取url，如果就没有插入图片，这里就是空的一个列表，[]
                for pic in media_pics:
                    media_urls.append('https:' + pic.get('src').replace('thumb180', 'bmiddle'))

                # 以uuid为键，拼接评论信息内容
                self.__comments[comment_id] = {'user_name': user_name,
                                               'user_url': user_url,
                                               'content': content,
                                               'time': comment_time,
                                               'media_urls': media_urls}

            # 获取评论，如果评论数已不增长，认为已尽可能获取评论，退出循环
            if last_len == len(self.__comments):
                break
            else:
                page += 1
                time.sleep(0.2)

    def run(self, limit=0, save_format='json'):
        self.__headers['cookie'] = self.cookie
        print('正在爬取主页上的微博……')
        self.__get_weibos()
        for i, weibos in enumerate(self.__weibos):
            for j, mid in enumerate(weibos[:limit] if limit != 0 else weibos):
                fn = '第{}页第{}条微博的评论'.format(i + 1, j + 1)
                print('正在爬取{}……'.format(fn))
                self.__get_comment_info(mid)
                if save_format == 'no':
                    print(json.dumps(self.__comments, ensure_ascii=False))
                elif save_format in ('json', 'txt'):
                    with open('{}.{}'.format(fn, save_format), mode='w', encoding="utf-8") as fp:
                        json.dump(self.__comments, fp, ensure_ascii=False)
                        print('……成功！')
                else:
                    csv_file = open('{}.csv'.format(fn), mode='w', encoding="utf-8-sig", newline='')
                    csv_writer = csv.writer(csv_file)

                    csv_header = ['评论uuid', '评论人用户名', '评论人微博链接',
                                  '评论内容', '评论时间', '带图评论的图片链接']
                    csv_writer.writerow(csv_header)

                    for key, value in self.__comments.items():
                        row = [', '.join(v) if isinstance(v, list) else v for k, v in value.items()]
                        row.insert(0, key)
                        csv_writer.writerow(row)
                    print('……成功！')
