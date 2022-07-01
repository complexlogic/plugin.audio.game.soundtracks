from bs4 import BeautifulSoup
import urllib
from .util import *

def page_end(tag):
    return tag.has_attr("class") and tag.has_attr("title") and tag["class"][0] == "pagenav" and tag["title"] == "End"

# Function to scrape the alphanumeric title pages
def alphabet(url):
    albums = list()
    pages = list()

    # Get first page
    page = get_page(url)
    if page is None:
        return albums
    pages.append(page)

    # Get the max page number
    max_page = 0
    item = page.find(page_end)
    if item is not None and item.has_attr("href"):
        max_page = int(urllib.parse.parse_qs(item["href"])["?page"][0])
    
    # Fetch remaining pages
    if (max_page > 1):
        for i in range(2, max_page + 1):
            page = get_page(url + "?" + urllib.parse.urlencode({"page": str(i)}))
            if page is not None:
                pages.append(page)

    # Album URL is in "href" attribute of "a" tag that is child of classless td tag
    for page in pages:
        for item in page.find_all('a'):
            url = str(item.get("href"))
            if item.parent.name == "td" and not item.parent.has_attr("class") and "/game-soundtracks/album/" in url:
                albums.append({"url": url, "title": item.string,
                            "playable": "false", "type": "album"})
    return albums

# Function to scrape platforms
def platform(url):
    platforms = list()
    page = get_page(url)
    if page is None:
        return platforms

    # Platform URL is in "href" attribute of "a" tag that is child of "div"
    for item in page.find_all('a'):
        url = str(item.get("href"))
        if "/game-soundtracks/" in url and item.parent.name == "div":
            platforms.append({"url": url,"title": item.string,
                              "playable": "false", "type": "album"})
    return platforms

# Function to scrape top 100 albums
def top100(url):
    albums = list()
    page = get_page(url)
    if page is None:
        return albums 

    # Album URL is in "href" attribute of "a" tag
    for item in page.find_all('a'):
        url = str(item.get("href"))
        if item.parent.name == "td" and not item.parent.has_attr("class") and "/game-soundtracks/album/" in url:
            albums.append({"url": url, "title": item.string,
                           "playable": "false", "type": "album"})
    return albums

# Function to scrape popular series
def popular_series(url):
    albums = list()
    page = get_page(url)
    if page is None:
        return albums

    # Series URL is in "href" attribute of a tag, that has "Popular Series" in
    # the string of the fourth parent's sibling "h3" tag
    for item in page.find_all("a", class_="mainlevel"):
        if (item.parent.parent.find_previous_sibling("h3").string == "Popular Series"):
            albums.append({"url": str(item.get("href")), "title": item.string,
                           "playable": "false", "type": "album"})
    return albums

# Function to scrape the songs in an album
def album(url):
    songs = list()
    urls = list()
    cover = ""

    page = get_page(url)
    if page is None:
        return songs
    # Song page URL is located in "href" attribute of "a" tag
    for item in page.find_all('a'):
        url = str(item.get("href"))
        if ((".png" in url or ".jpg" in url)
                and "https://vgmsite.com/soundtracks" in url and cover == ""):
            cover = url
        elif ".mp3" in url and url not in urls:
            urls.append(url)
            # If track number is present
            try:
                sibling = item.parent.find_previous_sibling("td").string
                track_number = int(sibling.split(".")[0])
                songs.append({"url": url, "title": item.string, "tracknumber":
                               track_number, "cover": cover, "playable": "true",
                               "type": "song"})
            # If track number is not present
            except:
                songs.append({"url": url, "title": item.string,
                              "playable": "true", "type": "song"})
    return songs

# Function to get the final URL of a song
def mp3(url):
    url = KHINSIDER_URL + url
    page = get_page(url)
    if page is None:
        return None

    # Audio file URL is located in "href" attribute of "a" tag
    for item in page.find_all('a'):
        url = str(item.get("href"))
        if "https://vgmsite.com/soundtracks/" in url and ".mp3" in url:
            return url
    return None