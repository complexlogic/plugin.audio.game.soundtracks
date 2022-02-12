import os
import sys
import urllib
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import requests
import sqlite3
from bs4 import BeautifulSoup

#static URLs
KHINSIDER_URL = "https://downloads.khinsider.com"
PLATFORM_URL = "https://downloads.khinsider.com/console-list"
TOP100_URL = "https://downloads.khinsider.com/last-6-months-top-100"
DB_FILE = "bookmarks.db"

#static alphabet directory
ALPHABET_DIRECTORY = ({'url': 'num', 'title': '#', 'playable': 'false'},
                      {'url': 'A', 'title': 'A', 'playable': 'false'},
                      {'url': 'B', 'title': 'B', 'playable': 'false'},
                      {'url': 'C', 'title': 'C', 'playable': 'false'},
                      {'url': 'D', 'title': 'D', 'playable': 'false'},
                      {'url': 'E', 'title': 'E', 'playable': 'false'},
                      {'url': 'F', 'title': 'F', 'playable': 'false'},
                      {'url': 'G', 'title': 'G', 'playable': 'false'},
                      {'url': 'H', 'title': 'H', 'playable': 'false'},
                      {'url': 'I', 'title': 'I', 'playable': 'false'},
                      {'url': 'J', 'title': 'J', 'playable': 'false'},
                      {'url': 'K', 'title': 'K', 'playable': 'false'},
                      {'url': 'L', 'title': 'L', 'playable': 'false'},
                      {'url': 'M', 'title': 'M', 'playable': 'false'},
                      {'url': 'N', 'title': 'N', 'playable': 'false'},
                      {'url': 'O', 'title': 'O', 'playable': 'false'},
                      {'url': 'P', 'title': 'P', 'playable': 'false'},
                      {'url': 'Q', 'title': 'Q', 'playable': 'false'},
                      {'url': 'R', 'title': 'R', 'playable': 'false'},
                      {'url': 'S', 'title': 'S', 'playable': 'false'},
                      {'url': 'T', 'title': 'T', 'playable': 'false'},
                      {'url': 'U', 'title': 'U', 'playable': 'false'},
                      {'url': 'V', 'title': 'V', 'playable': 'false'},
                      {'url': 'W', 'title': 'W', 'playable': 'false'},
                      {'url': 'X', 'title': 'X', 'playable': 'false'},
                      {'url': 'Y', 'title': 'Y', 'playable': 'false'},
                      {'url': 'Z', 'title': 'Z', 'playable': 'false'})

#static main menu directory
MAIN_MENU_DIRECTORY = ({'url': 'browse_title', 'title': 'Browse by Title', 'playable': 'false'},
                       {'url': 'browse_platform', 'title': 'Browse by Platform Name', 'playable': 'false'},
                       {'url': 'browse_series', 'title': 'Browse by Popular Series', 'playable': 'false'},
                       {'url': 'browse_top100', 'title': 'Browse Top 100', 'playable': 'false'},
                       {'url': 'display_bookmarks_main', 'title': 'Bookmarks', 'playable': 'false', 'type': 'directory'})

# Function to scrape the alphanumeric title pages
def alphabet_scraper(page):
    albums = []

    # Album URL is in "href" attribute of "a" tag that is child of "p"
    for item in page.find_all('a'):
        url = str(item.get("href"))
        if "/game-soundtracks/album/" in url and item.parent.name == "p":
            albums.append({"url": url,"title": item.string,
                           "playable": "false", "type": "album"})
    return albums

# Function to scrape platforms
def platform_scraper(page):
    platforms = []

    # Platform URL is in "href" attribute of "a" tag that is child of "div"
    for item in page.find_all('a'):
        url = str(item.get("href"))
        if "/game-soundtracks/" in url and item.parent.name == "div":
            platforms.append({"url": url,"title": item.string,
                              "playable": "false", "type": "album"})
    return platforms

# Function to scrape top 100 albums
def top100_scraper(page):
    albums = []

    # Album URL is in "href" attribute of "a" tag
    for item in page.find_all('a'):
        url = str(item.get("href"))
        if "/game-soundtracks/album/" in url:
            albums.append({"url": url, "title": item.string,
                           "playable": "false", "type": "album"})
    return albums

# Function to scrape popular series
def popular_series_scraper(page):
    albums = []

    # Series URL is in "href" attribute of a tag, that has "Popular Series" in
    # the string of the fourth parent's sibling "h3" tag
    for item in page.find_all('a'):
        url = str(item.get("href"))
        table_head = item.parent.parent.parent.parent.parent
        if "Popular Series" in table_head.find("h3").string:
            albums.append({"url": url,"title": item.string,
                           "playable": "false", "type": "album"})
    return albums

# Function to scrape the songs in an album
def album_scraper(page):
    songs = []
    urls = []
    cover = ""
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
def mp3_scraper(page):
    # Audio file URL is located in "href" attribute of "a" tag
    for item in page.find_all('a'):
        url = str(item.get("href"))
        if "https://vgmsite.com/soundtracks/" in url and ".mp3" in url:
            return url
    return None

# Function to build a URL to pass back to the plugin
def build_url(query):
    return base_url + '?' + urllib.parse.urlencode(query)

# Function to build a directory for kodi to display
def build_directory(items, mode):
    listitems = []
    for item in items:
        # If we are in bookmark view, set listitem path accordingly
        if mode == "display_bookmark_album":
            if item["type"] == "album":
                path = build_url({"mode": mode, "url": item["url"],
                                  "type": item["type"]})
            else:
                info = {"mode": "play", "url": item["url"], "type": item["type"]}
                if "cover" in item:
                    info["cover"] = item["cover"]

                path = build_url({"mode": "play", "url": item["url"], "type": item["type"]})
        # If not in bookmark view, set listitem path accordingly
        else:
            path = build_url({"mode": mode, "url": item["url"]})

        # Set listitem title and playability
        li = xbmcgui.ListItem(label=item["title"])
        li.setProperty('IsPlayable', item["playable"])

        # Set track number if available
        if "tracknumber" in item:
            li.setInfo("music", {"tracknumber": item["tracknumber"]})

        # Set cover art URL if available
        if "cover" in item and item["cover"] != "":
            cover = item["cover"].replace(" ", "%20")
            li.setArt({"icon": cover, "thumb": cover})

        # Set context menus for an album
        if ("type" in item and item["type"] == "album"
                and mode != "display_bookmark_album"):
            bookmark_url = build_url({"mode": "save_bookmark", "title": item["title"],
                                      "type": "album", "url": item["url"]})
            download_url = build_url({"mode": "download", "title": item["title"],
                                      "type": "album", "url": item["url"]})
            li.addContextMenuItems([('Add to Bookmarks', f'RunPlugin({bookmark_url})'),
                                    ('Download Album', f'RunPlugin({download_url})')])

        # Set context menu for a song
        elif ("type" in item and item["type"] == "song"
                and mode != "display_bookmark_album" and mode != "play_bookmark"):
            bookmark_info = {"mode": "save_bookmark", "title": item["title"], "type": "song", "url": item["url"]}
            download_info = {"mode": "download", "title": item["title"], "type": "song", "url": item["url"]}
            if "cover" in item:
                bookmark_info["cover"] = item["cover"]
                download_info["cover"] = item["cover"]
            if "tracknumber" in item:
                bookmark_info["tracknumber"] = item["tracknumber"]
                download_info["tracknumber"] = item["tracknumber"]
            bookmark_url = build_url(bookmark_info)
            download_url = build_url(download_info)
            li.addContextMenuItems([('Add to Bookmarks', f'RunPlugin({bookmark_url})'),
                                    ('Download Song', f'RunPlugin({download_url})')])

        # Send listitems to kodi
        if item["playable"] == "true":
            li.setInfo("music", {"title": item["title"]})
            listitems.append((path, li, False))
            xbmcplugin.setContent(addon_handle, 'songs')
        else:
            listitems.append((path, li, True))
            xbmcplugin.setContent(addon_handle, 'albums')

    # End the directory
    xbmcplugin.addDirectoryItems(addon_handle, listitems, len(listitems))
    xbmcplugin.endOfDirectory(addon_handle)

# Function to play the selected song
def play(url):
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

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

# Function to get the final URL for a song
def resolve_song_url(url):
    url = KHINSIDER_URL + url
    page = get_page(url)
    if page is None:
        return None
    return mp3_scraper(page)

# Function to get a list of songs in an album
def get_songs_from_album(url):
    url = KHINSIDER_URL + url
    page = get_page(url)
    if page is None:
        return None, 0
    songs = album_scraper(page)
    total_songs = len(songs)
    return songs, total_songs

# Function to display an album's songs
def display_songs(url):
    songs, total_songs = get_songs_from_album(url)
    if total_songs == 0:
        return
    progress_dialog = xbmcgui.DialogProgress()
    progress_dialog.create(addon_name,
                            message=f"Scraping track 1 of {total_songs}")

    # Get the final URL to the audio file
    for i in range(total_songs):
        if progress_dialog.iscanceled() == True:
            return None
        song_url = resolve_song_url(songs[i]["url"])
        if song_url is not None:
            songs[i]["url"] = song_url
        progress_dialog.update(100 * (i + 1) // total_songs,
                               f"Scraping track {i + 1} of {total_songs}")
    # Display songs
    if progress_dialog.iscanceled() == False:
        progress_dialog.close()
        build_directory(songs, "play")
    return songs

# A function to download a song
def download_song(output_dir, song):

    # Build filename
    filename = ""
    if "tracknumber" in song:
        track_number = str(song["tracknumber"])
        if song["tracknumber"] < 10:
            track_number = "0" + track_number
        filename = filename + track_number + " "
    filename += song["title"]
    extension = os.path.splitext(song["url"])[1]
    filename += extension

    # Download file
    response = http_request(song["url"])
    if response.status_code == 200:
        path = os.path.join(output_dir, filename).encode("utf-8")
        open(path, "wb").write(response.content)

# A function to download a song or album
def download(item):
    # Make sure a download location is set
    directory = xbmcaddon.Addon().getSettingString("download_location")
    if directory == "":
        answer = xbmcgui.Dialog().yesno(addon_name,
                                        "You must enter a download location in the settings before downloading a song or album. Would you like to do that now?")
        if answer is True:
            xbmcaddon.Addon().openSettings()
        return

    # If we are downloading a song
    if item["type"] == "song":
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(addon_name, f"Downloading {item['title']}")
        download_song(directory, item)
        progress_dialog.update(100)
        xbmcgui.Dialog().notification(addon_name, "Song Downloaded")

    # If we are downloading an album
    else:

        # Scrape album songs
        songs, total_songs = get_songs_from_album(item["url"])
        if total_songs == 0:
            return

        # Create album directory for the download
        output_dir = os.path.join(directory, item["title"])
        os.makedirs(output_dir, exist_ok=True)
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create(addon_name,
                               message=f"Downloading track 1 of {total_songs}")

        # Download songs
        for i in range(total_songs):
            if progress_dialog.iscanceled() == True:
                return
            song_url = resolve_song_url(songs[i]["url"])
            if song_url is not None:
                songs[i]["url"] = song_url
                download_song(output_dir, songs[i])
            progress_dialog.update(100 * (i + 1) // total_songs,
                                   f"Downloading track {i + 1} of {total_songs}")
        xbmcgui.Dialog().notification(addon_name, "Album Downloaded")

# Function to display titles by user-chosen letter
def display_albums_by_letter(url):
    if url == "num":
        url = "https://downloads.khinsider.com/game-soundtracks/browse/" + "%23"
    else:
        url = "https://downloads.khinsider.com/game-soundtracks/browse/" + url
    page = get_page(url)
    if page is None:
        return
    albums = alphabet_scraper(page)

    # Display albums
    build_directory(albums, "display_songs")

# Function to display available platforms
def display_albums_by_platform(url):
    url = KHINSIDER_URL + url
    page = get_page(url)
    if page is None:
        return
    albums = alphabet_scraper(page)

    # Display albums
    build_directory(albums, "display_songs")

# Function to display popular series
def display_albums_by_series(url):
    url = KHINSIDER_URL + url
    page = get_page(url)
    if page is None:
        return
    albums = alphabet_scraper(page)

    #Display albums
    build_directory(albums, "display_songs")

# Function to handle main menu presses
def display_category(url):

    # User pressed "Browse by Title"
    if url == "browse_title":
        build_directory(ALPHABET_DIRECTORY, "display_albums_by_letter")

    # User pressed "Browse by Platform"
    elif url == "browse_platform":
        page = get_page(PLATFORM_URL)
        if page is None:
            return
        platforms = platform_scraper(page)
        build_directory(platforms, "display_albums_by_platform")

    # User pressed "Browse by Popular Series"
    elif url == "browse_series":
        page = get_page(KHINSIDER_URL)
        if page is None:
            return
        popular_series = popular_series_scraper(page)
        build_directory(popular_series, "display_albums_by_series")

    # User pressed "Browse Top 100"
    elif url == "browse_top100":
        page = get_page(TOP100_URL)
        if page is None:
            return
        albums = top100_scraper(page)
        build_directory(albums, "display_songs")

    # User pressed "Bookmarks"
    elif url == "display_bookmarks_main":
        display_bookmarks(url)

# Function to save a bookmark
def save_bookmark(item):

    # Check if db exists
    os.makedirs(addon_dir, exist_ok=True)
    db_file = os.path.join(addon_dir, DB_FILE)
    db_exists =  os.path.isfile(db_file)

    # Open db, create tables if new db
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    if db_exists == False:
        cursor.execute("""CREATE TABLE directory
                         (title TEXT, type TEXT, url TEXT, cover TEXT, tracknumber INTEGER)""")
        cursor.execute("""CREATE TABLE album_songs
                          (album TEXT, title TEXT, album_url TEXT,
                           url TEXT, type TEXT, cover TEXT, tracknumber INTEGER)""")

    # Inform the user if album/song is already bookmarked
    cursor.execute ("SELECT title FROM directory WHERE url=?", (item["url"],))
    list = cursor.fetchall()
    if len(list) > 0:
        xbmcgui.Dialog().ok(addon_name,
                            f"This {item['type']} already exists in bookmarks.")
        return

    if item["type"] == "album":
        # Scrape album
        songs = display_songs(item["url"])
        if songs is not None:
            if "cover" in songs[0]:
                cover = songs[0]["cover"]
            else:
                cover = None

            # Insert album name into top-level directory db
            cursor.execute("""INSERT INTO directory VALUES
                              (?, ?, ?, ?, ?)""", (item["title"],
                                                   "album",
                                                   item["url"],
                                                   cover,
                                                   None))

            # Insert album's songs into subdirectory db
            for song in songs:
                if "tracknumber" not in song:
                    song["tracknumber"] = None
                cursor.execute("""INSERT INTO album_songs VALUES
                                  (?, ?, ?, ?, ?, ?, ?)""", (item["title"],
                                                             song["title"],
                                                             item["url"],
                                                             song["url"],
                                                             "song",
                                                             cover,
                                                             song["tracknumber"]))
                xbmcgui.Dialog().notification(addon_name, "Bookmark Added")

    # If user is bookmarking a song, insert song into top-level db
    else:
        if "tracknumber" not in item:
            item["tracknumber"] = None
        cursor.execute("INSERT INTO directory VALUES (?, ?, ?, ?, ?)", (item["title"],
                                                                        "song",
                                                                        item["url"],
                                                                        item["cover"],
                                                                        item["tracknumber"]))
        xbmcgui.Dialog().notification(addon_name, "Bookmark Added")

    # Save db, inform user
    conn.commit()
    cursor.close()
    conn.close()

# Function for viewing bookmarks
def display_bookmarks(url):
    db_file = os.path.join(addon_dir, DB_FILE)
    if os.path.isfile(db_file) == False:
        xbmcgui.Dialog().ok(addon_name,
                           ("No bookmarks found. Add bookmarks using the "
                            "context menu for an album or song."))
        return
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # If user entered from main menu, prepare top-level directory
    if url == "display_bookmarks_main":
        cursor.execute("SELECT * FROM directory")
        items = []
        for row in cursor.fetchall():
            item = row_to_dict(cursor, row)
            if item["cover"] is None:
                del item["cover"]
            if item["tracknumber"] is None:
                del item["tracknumber"]
            if item["type"] == "album":
                item["playable"] = "false"
            else:
                item["playable"] = "true"
            items.append(item)

        if len(items) == 0:
            xbmcgui.Dialog().ok(addon_name,
                               ("No bookmarks found. Add bookmarks using "
                                "the context menu for an album or song."))
        else:
            build_directory(items, "display_bookmark_album")

    # If user clicked on an album, diplay album's songs
    else:
        cursor.execute("SELECT * FROM album_songs WHERE album_url=?",(url,))
        items = []
        for row in cursor.fetchall():
            item = row_to_dict(cursor,row)
            if item["cover"] is None:
                del item["cover"]
            item["playable"] = "true"
            item["type"] = "song"
            items.append(item)
        build_directory(items, "play_bookmark")

# Function to delete bookmarks
def delete_bookmark():
    db_file = os.path.join(addon_dir,DB_FILE)

    if os.path.isfile(db_file) == False:
        xbmcgui.Dialog().ok(addon_name,
                           ("No bookmarks found. Add bookmarks using the "
                            "context menu for an album or song."))
    else:
        # Open db, check if there are items to delete
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT title, url, type FROM directory")
        items = []
        for item in cursor.fetchall():
            items.append([item[0], item[1], item[2]])
        if len(items) == 0:
            return

        # Get items to delete from user
        title_list = [item[0] for item in items]
        deletions = xbmcgui.Dialog().multiselect("Select Bookmark(s) for Removal", title_list)

        # Delete items chosen by user
        if deletions is not None:
            for i in deletions:
                url = items[i][1]
                type = items[i][2]
                cursor.execute("DELETE FROM directory WHERE url=?",(url,))
                if type == "album":
                    cursor.execute("DELETE FROM album_songs WHERE album_url=?",(url,))

        # Update db
        conn.commit()
        cursor.close()
        conn.close()

        # Notify user
        if deletions is not None:
            xbmcgui.Dialog().notification(addon_name, "Bookmark(s) deleted")

# Function to delete all bookmarks
def delete_all_bookmarks():
    # Open the db, inform the user if no bookmarks exist
    db_file = os.path.join(addon_dir, DB_FILE)
    if os.path.isfile(db_file) == False:
        xbmcgui.Dialog().ok(addon_name,
                           ("No bookmarks found. Add bookmarks using the "
                            "context menu for an album or song."))
    # Warn the user
    else:
        if(xbmcgui.Dialog().yesno(addon_name,
                                 ("Delete all bookmarks? "
                                  "This cannot be undone.")) == False):
            return

        # Delete all bookmarks
        else:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM directory")
            cursor.execute("DELETE FROM album_songs")
            conn.commit()
            cursor.close()
            conn.close()
            xbmcgui.Dialog().notification(addon_name,
                                          "All Bookmarks deleted")

# A function to convert an SQLite table row to a dictionary
def row_to_dict(cursor, row):
    d = {}
    for id, column in enumerate(cursor.description):
        d[column[0]] = row[id]
    return d

# Function to handle arguments
def handle_args():
    if "mode" in args:
        mode = args["mode"][0]
        url = args["url"][0]
        if mode == "play" or mode == "play_bookmark":
            play(url)
        elif mode == "display_songs":
            display_songs(url)
        elif mode == "display_albums_by_letter":
            display_albums_by_letter(url)
        elif mode == "display_albums_by_platform":
            display_albums_by_platform(url)
        elif mode == "display_albums_by_series":
            display_albums_by_series(url)
        elif mode == "save_bookmark":
            item = {"type": args["type"][0], "url": url, "title": args["title"][0]}
            if item["type"] == "song":
                if "cover" in args:
                    item["cover"] = args["cover"][0]
                else:
                    item["cover"] = None
                if "tracknumber" in args:
                    item["tracknumber"] = int(args["tracknumber"][0])
            save_bookmark(item)
        elif mode == "display_bookmark_album":
            display_bookmarks(url)
        elif mode == "download":
            item = {"type": args["type"][0], "url": url, "title": args["title"][0]}
            if item["type"] == "song" and "tracknumber" in args:
                item["tracknumber"] = int(args["tracknumber"][0])
            download(item)
        elif mode == "display_category":
            display_category(url)
    else:
        build_directory(MAIN_MENU_DIRECTORY, "display_category")

# Main function
if __name__ == '__main__':
    addon_dir = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
    addon_name = xbmcaddon.Addon().getAddonInfo('name')
    if sys.argv[1] == "delete_bookmark":
        delete_bookmark()
    elif sys.argv[1] == "delete_all_bookmarks":
        delete_all_bookmarks()
    else:
        base_url = sys.argv[0]
        addon_handle = int(sys.argv[1])
        args = urllib.parse.parse_qs(sys.argv[2][1:])
        handle_args()
