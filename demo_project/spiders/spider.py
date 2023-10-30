from demo_project.items import DemoProjectItem
from bs4 import BeautifulSoup
import requests
from json_formater import format
from collections import defaultdict
import json
import re
import scrapy
class MySpider(scrapy.Spider):
    name = 'my_spider'
    start_urls = ['https://almeera.online/']

    def parse(self, response):
        html_content = response.text
        image_url=response.css('.subcategory-icon')
        image_element = image_url.css('img')
        soup = BeautifulSoup(html_content, 'html.parser')
  
        category_to_subcategory = {}

        # Find all 'li' elements
        li_elements = soup.find_all('li')

        current_category = None
        current_subcategory = None

        for li in li_elements:
            a_element = li.find('a')
            if a_element:
                href = a_element.get('href')
                text = a_element.get_text()
                if 'class' in a_element.attrs and 'leaf' in a_element['class']:
                    if current_category:
                        if current_category not in category_to_subcategory:
                            category_to_subcategory[current_category] = []
                        category_to_subcategory[current_category].append(text)
                else:
                    # It's a category
                    current_category = text
                    category_to_subcategory[current_category] = []
        category_to_subcategory = {category: subcategories for category, subcategories in category_to_subcategory.items() if subcategories}
        
        link_list=[]
        for i in category_to_subcategory.keys():
            tmp_str='https://almeera.online/'+str(i)
            link_list.append(tmp_str)
        # print(link_list)
        base_url=[]
       
        image_urls = []
        url_list=link_list
        # print(url_list)
        sub_cat={}
        products=[]
        count=0
        sub_count=0
        print(category_to_subcategory)
        for url in category_to_subcategory.keys():
            try:
                link_url='https://almeera.online/'+str(url)
                link_url=link_url.replace(" ","%20")
                response = requests.get(link_url)
                val=category_to_subcategory[url]
                # print(val)
                # print(link_url)
                for i in val:
                    if  sub_count==85:
                        break
                    sub_count+=1
                    
                    sub_link_ = i.lower()
                    sub_link='https://almeera.online/'+str(sub_link_)
                    # print("=======")
                    # print(sub_link)
                    # print("=========")
                    sub_link=sub_link.replace("&", "and")
                    sub_link=sub_link.replace(" ", "-")
                    
                    sub_link=sub_link+str("-1")
                    response = requests.get(sub_link)
                    print("=============")
                    print(sub_link)
                    if response.status_code == 200:
                        page_content = response.text
                        soup_1 = BeautifulSoup(page_content, 'html.parser')
                        img_tags = soup_1.find_all('img',class_="photo")    
                        span_elements = soup_1.find_all('span', class_='price product-price')
                        sub_category=soup_1.find_all('span',class_="subcategory-name")
                        final_sub=[i.get_text()for i in sub_category]
                        sub_cat[url]=final_sub
                        test_product_name=[]
                        product_name=soup_1.find_all('h5',class_='product-name')
                        name_of_product=[span.get_text() for span in product_name]
                        product_list=[span.get_text() for span in span_elements ]
                        # print("===========")
                        # print(img_tags)
                        # print("========")

                        # image_url=[img_name.get('src') for img_name in img_tags]
                        image_url=[]
                        SKU_url=[]
                        name_of_product=[]
                        
                        for img in img_tags:
                            tmp_tag=img.get("src")
                            name_=img.get("alt")
                            pattern = r'(\d+)\.(jpg|png)'
                            match = re.search(pattern, str(tmp_tag))
                            print(tmp_tag)
                            if match:
                                number_str = match.group(1)
                                number = str(number_str)
                                if len(number)<5:
                                    SKU_url.append("None")
                                    pass
                                else:
                                    #print(number)
                                    SKU_url.append(number)
                                name_of_product.append(name_)
                            if tmp_tag.startswith('//'):
                                tmp_tag="https:"+tmp_tag
                                image_url.append(tmp_tag)
                            else:
                                tmp_tag="https://almeera.online/var/"+tmp_tag
                                image_url.append(tmp_tag)
                        product_data = [{
                                    "ItemTitle": product,
                                    "ItemPrice": price,
                                    "ItemImageURL": url_img,
                                    "SKU":sku
                                        }
                                    for product, price, url_img ,sku in zip(name_of_product[6::], product_list[6::], image_url[6::],SKU_url[6::])
                                    ]
                    print("==========")
                    print(str(url))
                    data_dict = {
                                "CategoryTitle": str(url),
                                "CategoryImageURL": str(link_url),
                                "Subcategories": [
                                    {"SubcategoryTitle": i,
                                        "Products": product_data}]}   
                    # print(image_url)
                    products.append(data_dict)
                    for img in img_tags[1:9]:
                        img_url = img.get('srcset')
                        if img_url:
                            final_url=img_url
                            try:
                                USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
                                original_string = final_url
                                modified_string = original_string.replace(" 2x", "")
                                response = requests.get(modified_string,USER_AGENT)
                                item = DemoProjectItem()
                                tmp_list=[]
                                tmp_list.append(modified_string)
                                item['image_urls'] = tmp_list
                                yield item
                            except:
                                pass
    
                            image_urls.append(final_url)
            except Exception as e:
                print(f"Error processing {url}: {e}")
            if count==55:
                break
            count+=1
        
        file_path = 'data.json'
        with open(file_path, 'w') as json_file:
            json.dump(products, json_file, indent=4)
        format(file_path)
