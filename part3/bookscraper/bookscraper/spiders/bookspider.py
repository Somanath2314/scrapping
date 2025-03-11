# import scrapy
# class BookspiderSpider(scrapy.Spider):
#     name = "bookspider"
#     allowed_domains = ["books.toscrape.com"]
#     start_urls = ["https://books.toscrape.com"]

#     def parse(self, response):
#         books = response.css('article.product_pod')
#         for book in books:
#             # yield{
#             #     "name":  book.css('h3 a::text').get(),
#             #     "price": book.css('.product_price .price_color::text').get(),
#                 # "url": book.css('h3 a').attrib['href']
#             # }
#             book_url = book.css('h3 a').attrib['href']
#             yield response.follow("https://books.toscrape.com/"+book_url, callback=self.parse_book)
#         next_page = response.css('li.next a').attrib['href']
#         if next_page is not None:
#             if 'catalogue/' in next_page:
#                 print("next page is catalogue")
#                 yield response.follow("https://books.toscrape.com/"+next_page, callback=self.parse)
#             else:
#                 yield response.follow("https://books.toscrape.com/catalogue/"+next_page, callback=self.parse) 


# import scrapy

# class BookspiderSpider(scrapy.Spider):
#     name = 'bookspider'
#     allowed_domains = ['books.toscrape.com']
#     start_urls = ['https://books.toscrape.com/']

#     def parse(self, response):
#         books = response.css('article.product_pod')
#         for book in books:
#             # yield{
#             #     'name' : book.css('h3 a::text').get(),
#             #     'price' : book.css('div.product_price .price_color::text').get(),
#             #     'url' : book.css('h3 a').attrib['href'],
#             # }
#         # //page 1 has <a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a>
#         # page 2 has <a href="in-her-wake_980/index.html" title="In Her Wake">In Her Wake</a>
#             base_url = book.css('h3 a').attrib['href']
#             if 'catalogue/' in base_url:
#                 book_url = 'https://books.toscrape.com/' + base_url
#             else:
#                 book_url = 'https://books.toscrape.com/catalogue/' + base_url
#             yield response.follow(book_url, callback=self.parse_book)
#         next_page = response.css('li.next a ::attr(href)').get()
#         if next_page is not None:
#             if 'catalogue/' in next_page:
#                 next_page_url = 'https://books.toscrape.com/' + next_page
#             else:
#                 next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
#             yield response.follow(next_page_url, callback=self.parse) 

#     def parse_book(self, response): 
#         content = {}
#         rows = response.css('table tr')
#         for tr in rows:
#             key1 = tr.css('th::text').get()
#             val1 = tr.css('td::text').get()
#             content[key1]= val1

#         yield{
#             "title":  response.css('#content_inner > article > div.row > div.col-sm-6.product_main > h1::text').get(),
#             "price": response.css('#content_inner > article > div.row > div.col-sm-6.product_main > p.price_color::text').get(), 
#             "rating": response.css('#content_inner > article > div.row > div.col-sm-6.product_main > p.star-rating').attrib['class'].split(' ')[1],
#             "content": content
#         }


import scrapy
from bookscraper.items import BookItem  

class BookspiderSpider(scrapy.Spider):
    name = 'bookspider'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']
    custom_settings = {
    'FEEDS': {
        'books.csv': {'format': 'csv', 'encoding': 'utf8'},
        'books.json': {'format': 'json', 'encoding': 'utf8'},
    }
}


    def parse(self, response):
        books = response.css('article.product_pod')
        for book in books:
            relative_url = book.css('h3 a').attrib['href']
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            yield scrapy.Request(book_url, callback=self.parse_book_page)

        ## Next Page        
        next_page = response.css('li.next a ::attr(href)').get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response):
        book = response.css("div.product_main")[0]
        table_rows = response.css("table tr")
        book_item = BookItem()
        book_item['url'] = response.url
        book_item['title'] = book.css("h1 ::text").get()
        book_item['upc'] = table_rows[0].css("td ::text").get()
        book_item['product_type'] = table_rows[1].css("td ::text").get()
        book_item['price_excl_tax'] = table_rows[2].css("td ::text").get()
        book_item['price_incl_tax'] = table_rows[3].css("td ::text").get()
        book_item['tax'] = table_rows[4].css("td ::text").get()
        book_item['availability'] = table_rows[5].css("td ::text").get()
        book_item['num_reviews'] = table_rows[6].css("td ::text").get()
        book_item['stars'] = book.css("p.star-rating").attrib['class']
        book_item['category'] = book.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get()
        book_item['description'] = book.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_item['price'] = book.css('p.price_color ::text').get()
        yield book_item
