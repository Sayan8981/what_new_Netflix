import scrapy 
from scrapy import *
import sys
import os
import time
import pinyin,unidecode
from scrapy import signals
from datetime import datetime,timedelta
from whats_new_netflix_crawler.items import *
sys.path.insert(0,os.getcwd()+'/xpath')
sys.path.insert(1,os.getcwd()+'/operation')
import create_db_tables
import xpath
import db_output
from db_output import db_output_stats
from send_mail import send_emails


class whatsnewnetflixbrowse(Spider):

    name="whatsnewnetflixbrowse"
    start_urls=["https://www.whats-on-netflix.com/"]

    #initialization:
    def __init__(self):
        self.item_category=''
        self.whats_new_url=''
        self.content_img='' 
        self.content_url=''  
        self.content_id=''
        self.content_type=''
        self.content_title=''
        self.season_number=''
        self.others_info_tags=[]
        self.content_show_type=''
        self.content_tv_rating=''
        self.content_description=''
        self.content_imdb_rating=''
        self.content_imdb_rating=''
        self.others_info_dict=dict()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(whatsnewnetflixbrowse, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    #TODO: to get the signal when spider closing
    def spider_closed(self, spider):
        #import pdb;pdb.set_trace()
        spider.logger.info('Spider closed: %s' % spider.name)
        # Whatever is here will run when the spider is done.
        print ("Preparing to create csv file from database...............")
        db_output_stats().main()
        time.sleep(10)
        print("Preparing to send email to client.................")
        send_emails().main()

    def cleanup(self):
        self.year='' 
        self.content_img='' 
        self.content_url=''  
        self.content_id=''
        self.content_type=''
        self.content_title=''
        self.season_number=''
        self.others_info_tags=[]
        self.content_show_type=''
        self.content_tv_rating=''
        self.content_description=''
        self.content_imdb_rating=''
        self.content_imdb_rating=''
        self.others_info_dict=dict() 

    def parse(self,response):
        sel=Selector(response)
        urls_node=sel.xpath('//ul[@id="menu-main"]/li/a/@href').extract()
        item_category_list=sel.xpath('//ul[@id="menu-main"]/li/a/text()').extract()
        for category in item_category_list:
            if category=='What’s New on Netflix':
                self.item_category=category
        for url in urls_node:
            if 'whats-new' in url:
                self.whats_new_url=url
                yield Request(url=self.whats_new_url,callback=self.parse_url,meta={'item_category':self.item_category},dont_filter = True)

    def parse_url(self,response):
        #import pdb;pdb.set_trace()
        yield Request(url=response.url,callback=self.pagination,meta={'item_category':response.meta['item_category']},dont_filter = True)
    
    #TODO: calling next_week_page and parse to next func
    def pagination(self,response):
        sel=Selector(response)
        yield Request(url=response.url,callback=self.content_scraped,meta={'item_category':response.meta['item_category']},dont_filter = True)   
        #import pdb;pdb.set_trace() 
        next_page=sel.xpath('//nav[@class="pagination group"]/ul/li[@class="next right"]/a/@href').extract_first()
        if next_page is not None:
            next_page_url="{}{}".format(''.join(self.whats_new_url),''.join(next_page))
            yield Request(url=next_page_url,callback=self.pagination,meta={'item_category':response.meta['item_category']},dont_filter = True)
    
    #TODO: data field to scrape 
    def content_scraped(self,response):
        #import pdb;pdb.set_trace()
        sel=Selector(response)
        #TODO: first take all titles from the coming page
        extract_titles=sel.xpath(xpath.title_xpath).extract()
        #TODO: Iterate through title to get the mata data for particular title 
        for title in extract_titles:
            self.cleanup()
            self.content_title=unidecode.unidecode(pinyin.get(title)).strip(' ')
            title=title.replace('\"','\'')
            self.content_img=sel.xpath(xpath.img_xpath%title).extract_first()
            self.content_imdb_rating=sel.xpath(xpath.imdb_rating_xpath%title).extract() 
            self.content_imdb_rating=tuple(filter(lambda rating: rating!='\n', self.content_imdb_rating))
            if self.content_imdb_rating:
                self.content_imdb_rating=self.content_imdb_rating[0].strip(' ')
            else:
                self.content_imdb_rating=''   
            self.content_url=sel.xpath(xpath.url_xpath%title).extract_first()     
            self.content_id=self.content_url.split('netflixid=')[-1:][0]
            self.content_type=sel.xpath(xpath.content_type_xpath%title).extract_first()
            self.content_show_type=sel.xpath(xpath.show_type_xpath%title).extract_first()
            if self.content_show_type=='TV Series':
                self.season_number=sel.xpath(xpath.season_number_xpath%title).extract_first().strip(' ()')    
            else:
                self.year=sel.xpath(xpath.year_xpath%title).extract_first().strip(' ()')
            self.content_tv_rating= sel.xpath(xpath.tv_rating_xpath%title).extract()     
            self.content_tv_rating=tuple(filter(lambda rating: rating!='\n' ,self.content_tv_rating))
            if self.content_tv_rating:
                self.content_tv_rating=self.content_tv_rating[0].replace('\n','').strip(' ')
            else:
                self.content_tv_rating=''    
            self.content_description=unidecode.unidecode(pinyin.get(sel.xpath(xpath.description_xpath%title).extract_first())).strip('\n')    
            self.others_info_tags=sel.xpath(xpath.other_info_xpath%title).extract() 
            if self.others_info_tags:
                for tags in self.others_info_tags:
                    self.others_info_dict[tags.strip(': ')]=sel.xpath(xpath.info_xpath%(title,tags)).get().strip(' ')
            print("\n")
            print({"content_title":self.content_title,"content_img_url":self.content_img,"content_imdb_rating":self.content_imdb_rating,"content_url":self.content_url,"content_id":self.content_id,"content_type":self.content_type,"content_show_type":self.content_show_type,"season_number":self.season_number,"year":self.year,"content_tv_rating":self.content_tv_rating,"content_description":self.content_description,"others_info":self.others_info_dict,"page_url":response.url})
            yield Request(url=response.url,meta={'item_category':response.meta['item_category'],"content_title":self.content_title,"content_img_url":self.content_img,"content_imdb_rating":self.content_imdb_rating,"content_url":self.content_url,"content_id":self.content_id,"content_type":self.content_type,"content_show_type":self.content_show_type,"season_number":self.season_number,"year":self.year,"content_tv_rating":self.content_tv_rating,"content_description":self.content_description,"others_info":self.others_info_dict,"page_url":response.url},callback=self.item_stored,dont_filter=True)

    def item_stored(self,response): 
        item=WhatsNewNetflixCrawlerItem()
        item["netflix_id"]=response.meta["content_id"]
        item["title"]=response.meta["content_title"]
        item["image"]=response.meta["content_img_url"]
        item["imdb_rating"]=response.meta["content_imdb_rating"]
        item["url"]=response.meta["content_url"]
        item["content_type"]=response.meta["content_type"]
        item["show_type"]=response.meta["content_show_type"]
        item["season_number"]=response.meta["season_number"]
        item["year"]=response.meta["year"]
        item["tv_rating"]=response.meta["content_tv_rating"]
        item["description"]=response.meta["content_description"]
        try:
            item["genre"]=response.meta["others_info"]["Genre"]
        except Exception:
            pass 
        try:       
            item["cast"]=response.meta["others_info"]["Cast"]
        except Exception:
            pass 
        try:       
            item["director"]=response.meta["others_info"]["Director"]
        except Exception:
            pass
        try:    
            item["runtime"]=response.meta["others_info"]["Runtime"]
        except Exception:
            pass
        try:        
            item["language"]=response.meta["others_info"]["Language"]
        except Exception:
            pass
        item["updated_db"]=datetime.now().strftime('%b %d, %Y')
        item["item_category"]=response.meta["item_category"]
        
           