# -*- coding: utf-8 -*-
import scrapy
from time import sleep
import random


class JobadvSpider(scrapy.Spider):
    name = 'jobadv'
    allowed_domains = ['ctgoodjobs.hk']
    start_urls = ['https://www.ctgoodjobs.hk/ctjob/listing/joblist.asp']
    

    def parse(self, response):
        path1 = '//div[@class="row jl-row jl-de"]'
        path2 = '//div[@class="row jl-row jl-pc"]'
        path3 = '//div[@class="row jl-row jl-pc active"]'
        path4 = '//div[@class="row jl-row jl-de active"]'
        
        listings = response.xpath(path1 + ' | ' + path2 + ' | ' + path3 + ' | ' + path4)

        for listing in listings:
            link = listing.xpath('.//div[@class="jl-title"]/h2/a/@href').extract_first()
            abs_link = response.urljoin(link)
            title = listing.xpath('.//div[@class="jl-title"]/h2/a/text()').extract_first()
            er = listing.xpath('.//a[@class="jl-comp-name"]/text()').extract_first()
            loc = listing.xpath('.//li[@class="loc col-xs-6"]/text()').extract()[1]
            exp = listing.xpath('.//li[@class="exp col-xs-6"]/text()').extract()[1]
            post_date = listing.xpath('.//li[@class="post-date col-xs-12"]/text()').extract()[1]
            
            yield scrapy.Request(abs_link,
                                callback=self.parse_listing,
                                meta={
                                     'abs_link' : abs_link,
                                     'title' : title,
                                     'er' : er,
                                     'loc' : loc,
                                     'exp' : exp,
                                     'post_date' : post_date
                                     })
            
            sleep(random.randrange(1,3))
            
        next_page_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
        
        if next_page_url:
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)
                
    def parse_listing(self, response):
        abs_link = response.meta['abs_link']
        title = response.meta['title']
        er = response.meta['er']
        loc = response.meta['loc']
        exp = response.meta['exp']
        post_date = response.meta['post_date']

        ref_no = response.xpath('//div[@class="col-sm-8 job-ref"]/text()').extract_first()

        content = response.xpath('//div[@class="jd-sec job-desc"]//descendant::*/text()').extract()

        for i in range(len(content)):
            content[i] = content[i].strip()

        content = ". ".join(content)
        content.strip()
        
        trs = response.xpath('//table[@class="table table-striped"]/tbody/tr')
        career_lv = trs[7].xpath('./td/ul/li/text()').extract_first()
        
        yield{
            'abs_link' : abs_link,
            'title' : title,
            'er' : er,
            'loc' : loc,
            'exp' : exp,
            'post_date' : post_date,
            'ref_no' : ref_no,
            'content' : content,
            'career_lv' : career_lv
            }
