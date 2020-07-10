import scrapy
import os
import urllib
import requests


class HairSpider(scrapy.Spider):
    name = 'hair_img'
    start_urls = [
        'https://www.thehairstyler.com/hairstyles/search?page=3&q=',
    ]

    def parse(self, response):
        
        data = response.css('div[class="card-body"]')

        for i in data:
            page_url = 'https://www.thehairstyler.com'+i.css('a::attr(href)').get()
            yield scrapy.Request(page_url, callback = self.parse_img_urls)


        # next_item = response.css('li[class="page-item d-none d-sm-block"]')
        # next_page = next_item.css('a[rel="next"]::attr(href)').get()
        # next_url = 'https://www.thehairstyler.com'+ next_page
        
        # if next_page is not None:
        #     yield response.follow(next_url, self.parse)
        
    def parse_img_urls(self, response):
        a = response.css('div[class="col-lg-6 col-md-12 col-xs-12 -hairstyle -full"]')
        list_img_url = a.css('img::attr(src)').getall()

        for img_url in list_img_url:
            https_url = 'https:'+img_url
            file_name = str(https_url.split('/')[-1])[0:-4]+'_'+https_url.split('/')[-4]+'.jpg'
            full_file_name = os.path.join('/img_folder', file_name)
            urllib.request.urlretrieve(https_url, full_file_name)