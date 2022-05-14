# Game Soundtracks
Game Soundtracks is a Kodi audio plugin for listening to and downloading video game music. The plugin scrapes the site [KHInsider](https://downloads.khinsider.com/), which hosts the most comprehensive collection of video game soundtracks available online.

## Installation
Download the latest [plugin.audio.game.soundtracks.zip](https://github.com/complexlogic/plugin.audio.game.soundtracks/releases/download/v1.0.1/plugin.audio.game.soundtracks.zip) file from the release page. In Kodi, navigate to Add-ons->Install from zip file, and select the zip file.

## Usage
Open the plugin from your add-on menu. The plugin contains several browsing modes for finding music:
- By game title, alphabetically
- By platform name
- By popular series
- By Top 100 albums

Additionally, the plugin has options to bookmark and download a song or album

### Bookmarks
Scraping an album can take anywhere from a few seconds to a few minutes depending on the number of tracks it contains. The bookmark feature stores the scraped URLs in a local database so the user doesn't need to scrape a frequently listened to song or album multiple times. Only the URLs are stored in the bookmark; the audio files are still streamed from the site during playback of a bookmark.

To save a bookmark, highlight a song or album and access the context menu by long pressing enter, then select "Add to Bookmarks". Your saved bookmarks may be viewed and selected for playback via the plugin's main directory, and bookmarks may be deleted in the plugin settings menu.

### Downloads
The plugin also has a download feature which will download a song or album to your local storage. The local files can then be added to your Kodi music library if you desire. The download location for the files must be set in the plugin settings. 

Similar to the bookmarking feature, the download option is in the context menu for a song or album, and can be accessed by long pressing enter on the highlighted item.
