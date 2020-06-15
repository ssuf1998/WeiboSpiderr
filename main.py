#!/usr/bin/env python
# encoding: utf-8
"""
@author: ssuf1998
@file: main.py
@time: 2020/6/15 14:42
@desc: Null
"""

from WeiboSpiderr import WeiboSpiderr

COOKIE = 'SINAGLOBAL=9048276103233.127.1592140173413; wb_view_log_6745017589=1536*8641.25; SCF=Aib7_YjR3pOGB4acCQjfu9AgaH9YqjLGH-91yi9AsEKeVDlMS2QgkokclNQ779zsA93kSKLXUX2mJPyB5UucDBA.; SUHB=0D-FcTW1iGP5nf; YF-V5-G0=bae6287b9457a76192e7de61c8d66c9d; _s_tentry=login.sina.com.cn; UOR=,,login.sina.com.cn; Apache=3085158169927.7173.1592198920179; ULV=1592198920230:2:2:2:3085158169927.7173.1592198920179:1592140173493; webim_unReadCount=%7B%22time%22%3A1592198923569%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A45%2C%22msgbox%22%3A0%7D; Ugrow-G0=6fd5dedc9d0f894fec342d051b79679e; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhCHg_V4VUwL0AU5Cfv9_Nq5JpVF02Re020S0-NeoBX; SUB=_2AkMpu4gldcPxrAVWnP0VzWznZIRH-jyabuHTAn7uJhMyAxh77lUXqSVutBF-XCCgVJMxlu8nzaUzHDBVc29GZ1Xn; login_sid_t=4350472db5e0a7bde8063fd958c86d1a; cross_origin_proto=SSL; WBStorage=42212210b087ca50|undefined; wb_view_log=1536*8641.25; YF-Page-G0=c704b1074605efc315869695a91e5996|1592198977|1592198904'

if __name__ == '__main__':
    spider = WeiboSpiderr(weibo_url='https://weibo.com/gugongweb', cookie=COOKIE)
    spider.run(limit=3, save_format='csv')
