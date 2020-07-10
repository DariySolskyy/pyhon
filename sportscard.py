import scrapy
import csv

class SportsCardSpider(scrapy.Spider):
    name = 'sportscard'
    start_urls = [
        'http://sportscarddatabase.com/CardSetList.aspx?sp=4',
    ]
    def parse(self, response):
        set_urls = response.xpath('//*[@id="ctl00_MainContent_lblSets"]/table/tr/td/ul/li/a/@href').extract()
        
        for item in set_urls:
            url = 'http://sportscarddatabase.com' + str(item)
        
            yield scrapy.Request(url, callback=self.parse_card)

    def parse_card(self, response):
        csv_list = []
        table = response.xpath('//*[@id="ctl00_MainContent_dgResults_dgResults"]/tr')
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        for row in table:
            data = {
                'Description': row.xpath('td[2]/a//text()').extract_first(),
                'Card url': 'http://sportscarddatabase.com' + str(row.xpath('td[2]/a/@href').extract_first()),
                'Attributes': row.xpath('td[3]/font/text()').extract_first(),
                'Print Run': row.xpath('td[4]/font/text()').extract_first()
            }
            csv_list.append(data)

        keys = ['Description', 'Card url', 'Attributes', 'Print Run']

        with open('hockey.csv', 'a+') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(csv_list)
