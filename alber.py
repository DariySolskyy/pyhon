# Author Dariy Solskyy
# Please pay attention to be ethical and legal

import scrapy
import json
import csv
import os.path
import re
import pandas as pd
from flatten_dict import flatten

class AlbertsonsSpider(scrapy.Spider):
    name = 'alber'

    # Defining request parameters for separate category (manually after visiting category webpage)
    category_url = 'https://www.albertsons.com/shop/aisles/wine-beer-spirits.177.html'
    category_name = 'wine-beer-spirits'
    category_id = '1_29'
    total_prod = 1903
    
    # Setting path and filenames for spider outcome
    path = '/Users/dariy/Coding/upwork/albertsons/'+category_name+'/'
    cat_base_file = path+'albertsons_'+category_name+'_base_only.csv'
    prod_det_file = path+'albertsons_'+category_name+'_products_only.csv'
    final_file = path+'albertsons_'+category_name+'.csv'

    # Requesting basic products' data from API
    def start_requests(self):

        starts = []
        for start in range (0, AlbertsonsSpider.total_prod, 200):
            starts.append(start)

            url = 'https://www.albertsons.com/abs/pub/xapi/search/products'
            
            # Headers and params taken from cURL
            headers = {
                'authority': 'www.albertsons.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'accept': 'application/json, text/plain, */*',
                'adrum': 'isAjax:true',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
                'ocp-apim-subscription-key': 'e914eec9448c4d5eb672debf5011cf8f',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': AlbertsonsSpider.category_url,
                'accept-language': 'en-US,en;q=0.9,ru;q=0.8,uk;q=0.7,da;q=0.6,de;q=0.5',
            }

            params = (
                ('request-id', '3892016269002'),
                ('url', 'https://www.albertsons.com'),
                ('pageurl', 'https://www.albertsons.com'),
                ('pagename', 'aisles'),
                ('rows', '200'),
                ('start', str(start)),
                ('search-type', 'category'),
                ('category-id', AlbertsonsSpider.category_id),
                ('storeid', '177'),
                ('featured', 'false'),
                ('search-uid', ''),
                ('q', ''),
                ('sort', ''),
                ('userid', ''),
                ('featuredsessionid', 'c9c9d3ba-93a8-49b4-bf54-63e65c8911f4'),
                ('screenwidth', '729'),
            )

            yield scrapy.FormRequest(url=url, method='GET', formdata=params, headers=headers, callback=self.base_list)

    # Parsing basic products'data from API, adding product and image url, creating category directory, saving data to CSV
    # This function calls back separate products parsing (parse_prod) function during the loop
    def base_list(self, response):
        
        resp_json = json.loads(response.text)
        products = resp_json['response']['docs']

        base_prod_list = []
        base_prod_list.extend(products)

        base_prod_url_list = []
        
        for i in base_prod_list:

            product_url = 'https://www.albertsons.com/shop/product-details.'+i['pid']+'.html'
            img_url = 'https://images.albertsons-media.com/is/image/ABS/'+i['pid']+'?$ecom-pdp-desktop$&defaultImage=Not_Available&defaultImage=Not_Available'
            i.update({'url':product_url})
            i.update({'img_url':img_url})
            base_prod_url_list.append(i)
            yield scrapy.Request(product_url, callback = self.parse_prod)
        
        cat_base_file = AlbertsonsSpider.cat_base_file
        os.makedirs(os.path.dirname(cat_base_file), exist_ok=True)
        file_exists = os.path.isfile(cat_base_file)

        columns_base = ['price', 'unitOfMeasure', 'sellByWeight', 'aisleName', 'name', 'departmentName', 'pid', 'aisleId', 'upc', 'restrictedValue', 'displayType', 'basePrice', 'averageWeight', 'pricePer', 'salesRank', 'shelfName', 'id', 'promoDescription', 'promoType', 'url', 'img_url']

        with open(cat_base_file, 'a+') as file:
            writer = csv.DictWriter(file, fieldnames=columns_base, dialect='excel', extrasaction='ignore')
            if not file_exists:
                writer.writeheader()
            for line in base_prod_url_list:
                writer.writerow(line)
    
    # Parsing data from each separate product page using xPATH and pandas, saving data to CSV
    def parse_prod(self, response):

        prod_list = []
            
        try:
            Ingredients = ' '.join((response.xpath('//*[@id="ingredients"]/div/div[2]/text()').get()).split())
        except:
            Ingredients = ' '.join((response.xpath('//*[@id="ingredients"]/div/div/text()').get()).split())

        try:
            Details_short = ' '.join((response.xpath('//*[@id="details"]/div/div[1]/text()').get()).split())
        except:
            Details_short = None
        
        try:
            Details_long = ' '.join((response.xpath('//*[@id="details"]/div/div[2]/text()').get()).split())
        except:
            Details_long = None

        try:
            Serving_Size = re.search(r'(?<=Serving Size: ).*', response.xpath('//table[@class="tableOfIngredients"]/tbody/tr[1]/td/span[1]/text()').get()).group()
        except:
            Serving_Size = None

        try:
            Servings_Per_Container = re.search(r'(?<=Servings Per Container:  ).*', response.xpath('//table[@class="tableOfIngredients"]/tbody/tr[1]/td/span[2]/text()').get()).group()
        except:
            Servings_Per_Container = None

        #General product data
        data = {
            'pid': re.search(r'\d+', response.xpath('/html/head/link/@href').get()).group(),
            'Product Name': response.css('h2[class="modal-heading"]::text').get(),
            'Company Name': response.xpath('//span[contains(string(), "About the Producer")]/following-sibling::span/text()').get(),
            'Ingredients': Ingredients,
            'Warning': response.xpath('//span[contains(string(), "Warning")]/following-sibling::span/text()').get(),
            'Details short': Details_short,
            'Details long': Details_long,
            'Attributes': response.xpath('//span[contains(string(), "Product Attributes")]/following-sibling::span/div/text()').extract() ,
            'Directions': response.xpath('//span[contains(string(), "Directions")]/following-sibling::span/text()').get(),
            'Disclaimer': response.xpath('//span[contains(string(), "Disclaimer")]/following-sibling::span/div/div/div/div/p/text()').get(),
        }
        
        #Serving data
        serving = {
            'Serving Size': Serving_Size,
            'Servings Per Container': Servings_Per_Container,
        }
        data.update(serving)
        
        #Nutritional table
        try:
            table = response.xpath('//table[@class="tableOfIngredients"]').get()
            
            #Create DataFrame from html Ingredients table
            df = pd.read_html(table, header=0)[0]
            
            #Assign new column names
            df.columns=["Type", "Amount", "Daily %"] 
            
            #Clean data (case insensitive)
            df[df.columns[1]] = df[df.columns[1]].str.replace(r'Amount Per serving', '', regex=True, flags=re.IGNORECASE)
            df[df.columns[2]] = df[df.columns[2]].str.replace(r'% Daily Value', '', regex=True, flags=re.IGNORECASE)

            #Remove whitespaces in data
            df[df.columns[1]] = df[df.columns[1]].str.strip()
            print(df.index)

            #Create a dictionary from DataFrame
            unindexed = df.set_index(df.columns[0])
            nested_nutr_dict = unindexed.to_dict('index')
            nutr_dict = flatten(nested_nutr_dict, reducer='underscore')
        
            data.update(nutr_dict)
        except:
            None
        
        #Add data to list of products
        prod_list.append(data)
        
        prod_det_file = AlbertsonsSpider.prod_det_file
        os.makedirs(os.path.dirname(prod_det_file), exist_ok=True)
        file_exists = os.path.isfile(prod_det_file)

        columns_prod = ['pid', 'Product Name', 'Company Name', 'Ingredients', 'Warning', 'Details short', 'Details long', 'Attributes', 'Directions', 'Disclaimer', 'Serving Size', 'Servings Per Container', 'Calories_Amount', 'Calories_Daily %', 'Calories From Fat_Amount', 'Calories From Fat_Daily %', 'Total Fat_Amount', 'Total Fat_Daily %', 'Saturated Fat_Amount', 'Saturated Fat_Daily %', 'Trans Fat_Amount', 'Trans Fat_Daily %', 'Polyunsaturated Fat_Amount', 'Polyunsaturated Fat_Daily %', 'Monounsaturated Fat_Amount', 'Monounsaturated Fat_Daily %', 'Cholesterol_Amount', 'Cholesterol_Daily %', 'Sodium_Amount', 'Sodium_Daily %', 'Potassium_Amount', 'Potassium_Daily %', 'Total Carbohydrate_Amount', 'Total Carbohydrate_Daily %', 'Dietary Fiber_Amount', 'Dietary Fiber_Daily %', 'Sugars_Amount', 'Sugars_Daily %', 'Protein_Amount', 'Protein_Daily %', 'Vitamin A_Amount', 'Vitamin A_Daily %', 'Vitamin C_Amount', 'Vitamin C_Daily %', 'Calcium_Amount', 'Calcium_Daily %', 'Iron_Amount', 'Iron_Daily %']
        
        with open (prod_det_file, 'a+') as file:
            writer = csv.DictWriter(file, fieldnames=columns_prod, dialect='excel', extrasaction='ignore')
            if not file_exists:
                writer.writeheader()
            writer.writerows(prod_list)
    
    # Merging two CSVs after spyder finishes
    def closed(self, reason):

        left = pd.read_csv(AlbertsonsSpider.cat_base_file, dtype={'upc': str, 'id':str})
        right = pd.read_csv(AlbertsonsSpider.prod_det_file)

        merged_data = pd.merge(left.drop_duplicates(), right, on='pid')
        
        os.makedirs(os.path.dirname(AlbertsonsSpider.final_file), exist_ok=True)
        merged_data.to_csv(AlbertsonsSpider.final_file, index=False)