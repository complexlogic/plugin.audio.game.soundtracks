import requests
from .defines import *
from bs4 import BeautifulSoup
from . import scrapers as scraper

# Function to perform HTTP requests
def http_request(url):
    useragent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                 "AppleWebKit/537.36 (KHTML, like Gecko) "
                 "Chrome/90.0.4430.212 Safari/537.36")
    headers = {"User-Agent": useragent}
    return requests.get(url, headers=headers)

# Function to download a web page and convert to Beautiful Soup object
def get_page(url):
    response = http_request(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text,"html.parser")
    else:
        return None
