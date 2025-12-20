import logging

from scraper.browser import BrowserSession  # or wherever you saved your class
from scraper.orchestrator import scrape_listings
from scraper.parser import *
from app.orchestrator import *

# logging.basicConfig(
#     level=logging.DEBUG,  # Show DEBUG and higher level messages
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
#
# urls = ["https://www.vinted.co.uk/catalog?search_text=stussy+shirt&order=newest_first&page=1"]
#
# collect_listings(urls, '/home/opc/vinted-scraper-2/storage/test.h5')

hd5 = HDF5Storer('/home/opc/vinted-scraper-2/storage/test.h5')
hd5.read_dataset(5)