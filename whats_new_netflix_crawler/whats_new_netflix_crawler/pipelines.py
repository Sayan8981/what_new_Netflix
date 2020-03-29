# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import os
import sys
import db_detail


class WhatsNewNetflixCrawlerPipeline(object):
   def __init__(self):
        self.connection=MySQLdb.connect(host=db_detail.IP_addr,user='%s'%db_detail.username,passwd='%s'%db_detail.passwd,db='%s'%db_detail.database_name,charset="utf8", use_unicode=True)
        self.cursor=self.connection.cursor() 
        self.counter=0

   def process_item(self, item, spider):
        #import pdb;pdb.set_trace()  
        self.query="insert into netflix (netflix_id,title,image,rating,url,content_type,show_type,season_number,year,tv_rating,description,genre,cast,director,duration,language,updated_db,item_category) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        self.cursor.execute(self.query,(item["netflix_id"],item["title"],item["image"],item["rating"],item["url"],item["content_type"],item["show_type"],item["season_number"],item["year"],item["tv_rating"],item["description"],item["genre"],item["cast"],item["director"],item["runtime"],item["language"],item["updated_db"],item["item_category"]))
        self.counter+=1
        self.connection.autocommit(True)
        print("\n")
        print ("Total commit: ", self.counter)
        print("\n")
        return item