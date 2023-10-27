from demo_project.items import DemoProjectItem
from bs4 import BeautifulSoup
import requests
from json_formater import format
from collections import defaultdict
import json
import scrapy
class MySpider(scrapy.Spider):
    name = 'my_spider'
    start_urls = ['https://almeera.online/']

    def parse(self, response):
        html_content = response.text
        image_url=response.css('.subcategory-icon')
        image_element = image_url.css('img')
        soup = BeautifulSoup(html_content, 'html.parser')
        urls = soup.find_all('a')
        
        category={}
        leaf_of_sub=soup.find_all('ul',class_="subcategory-view-icons subcategory-list grid-list clearfix")
        category_to_subcategory = {}

        # Find all 'li' elements
        li_elements = soup.find_all('li')

        current_category = None
        current_subcategory = None

        for li in li_elements:
            # Check if the 'li' element contains an 'a' element
            a_element = li.find('a')
            if a_element:
                # Extract the 'href' attribute and text content
                href = a_element.get('href')
                text = a_element.get_text()

                # Determine whether it's a category or subcategory
                if 'class' in a_element.attrs and 'leaf' in a_element['class']:
                    # It's a subcategory
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
        print(link_list)
        base_url=[]
       
        image_urls = []
        # # url_list=['https://almeera.online/','https://almeera.online/fruits-and-vegetables-2/','https://almeera.online/meat-and-seafood-1/']
        url_list=link_list
        # print(url_list)
        sub_cat={}
        products=[]
        count=0
        sub_count=0
        for url in category_to_subcategory.keys():
            try:
                link_url='https://almeera.online/'+str(url)
                link_url=link_url.replace(" ","%20")
                response = requests.get(link_url)
                val=category_to_subcategory[url]
                for i in val:
                    if  sub_count==50:
                        break
                    sub_count+=1
                    sub_link='https://almeera.online/'+str(i)
                    sub_link=sub_link.replace(" ", "%20")
                    print(sub_link)
                    response = requests.get(sub_link)
                    if response.status_code == 200:
                        page_content = response.text
                        soup = BeautifulSoup(page_content, 'html.parser')
                        img_tags = soup.find_all('img')    
                        span_elements = soup.find_all('span', class_='price product-price')
                        sub_category=soup.find_all('span',class_="subcategory-name")
                        final_sub=[i.get_text()for i in sub_category]
                        sub_cat[url]=final_sub
                        product_name=soup.find_all('h5',class_='product-name')
                        name_of_product=[span.get_text() for span in product_name]
                        product_list=[span.get_text() for span in span_elements ]
                        default_url =  "https://almeera.online/var/images/product/400.440/9918802000000.jpg 2x"
                        # image_url=[img_name.get('src') for img_name in img_tags]
                        image_url=[]
                        for img in img_tags:
                            tmp_tag=img.get("src")
                            if tmp_tag.startswith('//'):
                                tmp_tag="https:"+tmp_tag
                                image_url.append(tmp_tag)
                            else:
                                tmp_tag="https://almeera.online/var/"+tmp_tag
                                image_url.append(tmp_tag)
                        product_data = [{
                                    "ItemTitle": product,
                                    "ItemPrice": price,
                                    "ItemImageURL": url_img
                                        }
                                    for product, price, url_img in zip(name_of_product, product_list, image_url)
                                    ]
                    data_dict = {
                                "CategoryTitle": str(url),
                                "CategoryImageURL": str(link_url),
                                "Subcategories": [
                                    {"SubcategoryTitle": i,
                                        "Products": product_data}]}   
                
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
            if count==50:
                break
            count+=1
        
        file_path = 'data.json'
        with open(file_path, 'w') as json_file:
            json.dump(products, json_file, indent=4)
        format(file_path)
