#!/usr/bin/env python
# encoding: utf-8
"""
@author: ssuf1998
@file: WeiboSpiderr.py
@time: 2020/6/15 14:29
@desc: Null
"""

import json
import re
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

from util import get_abs_time, clean_content, get_arg, multi_format_output


class WeiboSpiderr(object):
    def __init__(self, weibo_url, cookie):
        self.__WEIBO_DETAIL_API = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&id={mid}&page={page}&filter=all&from=singleWeiBo&__rnd={timestamp}'
        self.__WEIBOS_LIST_API = '{weibo_url}?page={page}'
        self.__UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
        self.__INTERVAL = 0.5
        self.__RETRY_TIMES = 5
        self.__COMMENT_NUM_THRESHOLD = 1.0
        self.__headers = {
            'user-agent': self.__UA,
            'cookie': ''
        }

        self.cookie = cookie
        self.weibo_url = weibo_url

        self.__comments = {}
        self.__weibo_detail = {}

    def __get_weibo_info(self, page=1):
        self.__weibo_detail.clear()

        request = requests.get(
            url=self.__WEIBOS_LIST_API.format(weibo_url=self.weibo_url, page=page),
            headers=self.__headers)
        request.encoding = 'utf-8'
        bs = BeautifulSoup(request.text, 'lxml')

        for script in bs.select('script'):
            weibo_json_str = re.search(r'(?<=FM.view\()(.*)(?=\))', str(script))
            if weibo_json_str:
                weibo_json_obj = json.loads(weibo_json_str.group())
                if 'Pl_Official_MyProfileFeed' in weibo_json_obj['domid']:
                    bs = BeautifulSoup(weibo_json_obj['html'], 'lxml')
                    break

        weibos = bs.select('div[mid].WB_cardwrap')

        for weibo in weibos:
            weibo_content = clean_content(weibo, prefix='>').replace('\u200b', '').strip()
            weibo_send_time = weibo.select_one('a[node-type="feed_list_item_date"]').getText().strip()
            weibo_send_time = get_abs_time(weibo_send_time)
            weibo_detail_url = 'https://weibo.com' + weibo.select_one('a[node-type="feed_list_item_date"]').get('href')
            weibo_transfer_num = weibo.select_one('span[node-type="forward_btn_text"]').getText().strip()[1:]
            weibo_comment_num = weibo.select_one('span[node-type="comment_btn_text"]').getText().strip()[1:]
            weibo_like_num = weibo.select_one('span[node-type="like_status"]').getText().strip()[1:]

            weibo_media_urls = []
            weibo_media_pics = weibo.select('div .WB_media_wrap .WB_pic img')
            for pic in weibo_media_pics:
                weibo_media_urls.append('https:' + pic.get('src').replace('thumb180', 'mw690'))

            weibo_media_videos = weibo.select('div .WB_media_wrap .WB_video')
            for video in weibo_media_videos:
                get_str = urllib.parse.unquote(video.get('action-data'))
                weibo_media_urls.append(get_arg(get_str, 'short_url'))

            self.__weibo_detail[weibo.get('mid')] = {
                'content': weibo_content,
                'send_time': weibo_send_time,
                'detail_url': weibo_detail_url,
                'transfer': weibo_transfer_num,
                'comment': weibo_comment_num,
                'like': weibo_like_num,
                'media_urls': weibo_media_urls
            }
        time.sleep(self.__INTERVAL)

    def __get_comment_info(self, mid):
        self.__comments.clear()
        page = 1
        while True:
            last_len = len(self.__comments)
            request = requests.get(
                url=self.__WEIBO_DETAIL_API.format(
                    mid=mid,
                    page=page,
                    timestamp=int(round(time.time() * 1000))),
                headers=self.__headers)
            request.encoding = 'utf-8'

            bs = BeautifulSoup(request.json()['data']['html'], 'lxml')

            count = request.json()['data']['count']

            # 逐条评论爬取
            for wrap in bs.select('div[node-type="comment_list"]>[comment_id]'):
                # 评论uuid，用作键值
                comment_id = wrap.get('comment_id')

                # 评论人用户名
                user_name = wrap.select_one('a[usercard]').getText()
                # 评论人微博主页链接
                user_url = 'https:' + wrap.select_one('a[usercard]').get('href')
                # 评论内容

                content = clean_content(wrap)

                # 评论时间格式化，将“今天”转化为日期
                comment_time = get_abs_time(wrap.select_one('div .WB_from.S_txt2').getText())

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
                                               'media_urls': media_urls,
                                               'mid': mid}

            # 获取评论
            if count in range(int(len(self.__comments) * self.__COMMENT_NUM_THRESHOLD),
                              len(self.__comments)):
                break
            else:
                if page > self.__RETRY_TIMES and last_len == len(self.__comments):
                    break
                else:
                    page += 1
                    time.sleep(self.__INTERVAL)

    def run(self, limit=0, page_range=(1, 1), save_format='json'):
        self.__headers['cookie'] = self.cookie

        for i in range(page_range[0], page_range[1] + 1):
            fn = '第{}页上的微博详情'.format(i)
            print('正在爬取{}……'.format(fn))
            self.__get_weibo_info(page=i)

            multi_format_output(save_format,
                                fn,
                                ['微博id', '微博内容', '发布时间',
                                 '微博链接', '转发量', '评论量',
                                 '点赞量', '媒体链接'],
                                self.__weibo_detail)
            print('……成功！')

            mids = list(self.__weibo_detail.keys())
            for j, mid in enumerate(mids[:limit] if limit != 0 else mids):
                fn = '第{}页第{}条微博的评论'.format(i, j + 1)
                print('正在爬取{}……'.format(fn))
                self.__get_comment_info(mid)
                multi_format_output(save_format,
                                    fn,
                                    ['评论id', '评论人昵称', '评论人微博主页链接',
                                     '评论内容', '发布时间', '媒体链接',
                                     '所属微博id'],
                                    self.__comments)
                print('……成功！')
