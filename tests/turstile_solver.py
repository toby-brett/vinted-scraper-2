# pip install zenrows
from zenrows import ZenRowsClient
from scraper.parser import *
from bs4 import BeautifulSoup

client = ZenRowsClient("4657366a97ff86ac46a338dba5799e8cbbb7738c")
url = "https://www.vinted.co.uk/catalog?search_text=stussy%20teeshirt&search_id=29654630613"

response = client.get(url)
print(response.text)
soup = BeautifulSoup(response.text, 'lxml')

listings_soup = Parser.parse_page(soup)
for listing in listings_soup:
    lst = Parser.parse_listing(listing)
print(lst)