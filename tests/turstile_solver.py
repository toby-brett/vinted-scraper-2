# pip install zenrows
from scraper.browser import *

with BrowserSession() as session:
    url = "https://www.vinted.co.uk/catalog?search_text=tshirt"
    soup = session.fetch_html(url)
    if soup:
        print(soup.prettify()[2000])  # first 1000 chars
