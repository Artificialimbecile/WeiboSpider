#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random
import sys
import traceback
from time import sleep

import requests
from lxml import etree
from tqdm import tqdm

from weibo import Weibo


class Follow(object):
    def __init__(self, user_id, cookie):
        """Follow类初始化"""
        if not isinstance(user_id, int):
            sys.exit(u'user_id值应为一串数字形式,请重新输入')
        self.user_id = user_id
        self.cookie = cookie
        self.follow_list = [str(user_id)]   # 存储爬取到的所有关注微博的user_id
        self.follow_name_list = []          # 存储爬取到的所有关注微博的用户名

    def deal_html(self, url):
        """处理html"""
        try:
            html = requests.get(url, cookies=self.cookie).content
            selector = etree.HTML(html)
            return selector
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def get_page_num(self):
        """获取关注列表页数"""
        url = "https://weibo.cn/%d/follow" % self.user_id
        selector = self.deal_html(url)
        user_name = selector.xpath('//div[@class="ut"]/text()')[0]
        user_name = user_name[:user_name.find('关注')]  # 获取user_name
        self.follow_name_list.append(user_name)
        if selector.xpath("//input[@name='mp']") == []:
            page_num = 1
        else:
            page_num = (int)(
                selector.xpath("//input[@name='mp']")[0].attrib['value'])
        return page_num

    def get_one_page(self, page):
        """获取第page页的user_id"""
        url = 'https://weibo.cn/%d/follow?page=%d' % (self.user_id, page)
        selector = self.deal_html(url)

        table_list = selector.xpath('//table')
        for t in table_list:
            # im = t.xpath('.//a/@href')[-1]
            im = t.xpath('.//a/@href')[0]           # 获取uid
            name = t.xpath('.//a/text()')[0]        # 获取用户名
            user_id = im[im.find('u') + 2:]         # 截取uid
            img = t.xpath('.//img/@src')            # 获取图片，如果有两个图片，第二个图片是大V
            peoples = t.xpath('.//td/text()')       # 获取粉丝数
            for people in peoples:
                if people.find("粉丝") == 0:
                    num_people = people[2:people.find("人")]
                    break
            if user_id.isdigit() and len(img) <= 1 and int(num_people) < 1000:
                self.follow_list.append(user_id)
                self.follow_name_list.append(name)

    def get_follow_list(self):
        """获取关注用户主页地址"""
        page_num = self.get_page_num()
        print(u'用户关注页数：' + str(page_num))
        page1 = 0
        random_pages = random.randint(1, 5)
        for page in tqdm(range(1, page_num + 1), desc=u'关注列表爬取进度'):
            self.get_one_page(page)

            if page - page1 == random_pages and page < page_num:
                sleep(random.randint(6, 10))
                page1 = page
                random_pages = random.randint(1, 5)

        print(u'用户关注列表爬取完毕')


def main():
    try:
        # 爬取关注列表的user_id
        user_id = 'Your id'
        cookie = {'Cookie': 'Your cookie'}
        # 将your cookie替换成自己的cookie
        fw = Follow(user_id, cookie)    # 调用Weibo类，创建微博实例wb
        fw.get_follow_list()            # 获取关注列表
        print(fw.follow_list)           # 输出关注列表的uid
        print(fw.follow_name_list)      # 输出关注列表的昵称

        filter = 1  # 值为0表示爬取全部微博（原创微博+转发微博），值为1表示只爬取原创微博
        since_date = '2018-01-01'  # 起始时间，即爬取发布日期从该值到现在的微博，形式为yyyy-mm-dd
        """mongodb_write值为0代表不将结果写入MongoDB数据库,1代表写入；若要写入MongoDB数据库，
        请先安装MongoDB数据库和pymongo，pymongo安装方法为命令行运行:pip install pymongo"""
        mongodb_write = 0
        """mysql_write值为0代表不将结果写入MySQL数据库,1代表写入;若要写入MySQL数据库，
        请先安装MySQL数据库和pymysql，pymysql安装方法为命令行运行:pip install pymysql"""
        mysql_write = 0
        pic_download = 1  # 值为0代表不下载微博原始图片,1代表下载微博原始图片
        video_download = 0  # 值为0代表不下载微博视频,1代表下载微博视频
        for user in fw.follow_list:
            # 爬每个人的微博
            new_list = [user]
            wb = Weibo(filter, since_date, mongodb_write, mysql_write, pic_download, video_download)
            wb.start(new_list)

    except Exception as e:
        print('Error: ', e)
        traceback.print_exc()


if __name__ == '__main__':
    main()
