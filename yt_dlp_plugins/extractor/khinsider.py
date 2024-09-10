#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import clean_html, ExtractorError
import re

class KHInsiderTrackIE(InfoExtractor):
    __version__ = "0.1.0"
    _WORKING = True
    IE_NAME = "khinsider_track"
    IE_DESC = "Bur's KHInsider VGM Downloader [Downloads tracks in mp3]"
    IE_BUG_REPORT = "Please report this issue on https://github.com/burandby/bursytdlps"
    
    _VALID_URL = r'https?://downloads\.khinsider\.com/game-soundtracks/album/[^/]+/(?P<id>[\w.%]+)'
    _TESTS = [
        {
            'url': 'https://downloads.khinsider.com/game-soundtracks/album/acquaria-windows-gamerip-2003/01.%2520Acquaria-Theme.mp3',
            'info_dict': {
                'id': '01.%2520Acquaria-Theme.mp3',
                'title': 'Acquaria-Theme',
                'ext': 'mp3',
            }
        }
    ]
    
    def _real_extract(self, url):
        webpage = self._download_webpage(url, None)
        
        # Extract song title
        title = self._html_search_regex(r'Song name:\s*(.*)', webpage, 'song title', default=None)
        id = url.split('/')[-1]
        
        audio = self._html_search_regex(r'<audio.*?src="([^"]+)"', webpage, 'MP3 URL', default=None)
        if not audio:
            raise ExtractorError('Could not find MP3 URL')
        
        return {
            'id': id,
            'title': title,
            'url': audio,
            'ext': 'mp3',
        }
        

class KhinsiderAlbumIE(InfoExtractor):
    __version__ = "0.1.0"
    _WORKING = True
    IE_NAME = "khinsider:album"
    IE_DESC = "Bur's KHInsider VGM Downloader [Downloads albums in MP3]"
    IE_BUG_REPORT = "Please report this issue on https://github.com/burandby/bursytdlps"
    
    _VALID_URL = r'https?://downloads\.khinsider\.com/game-soundtracks/album/(?P<id>[\w-]+)'
    _TESTS = [
        {
            'url': 'https://downloads.khinsider.com/game-soundtracks/album/drawful-2-original-unofficial-soundtrack-family-computer-ios-linux-macos-ps4-gamerip-2016',
            'info_dict': {
                'id': 'drawful-2-original-unofficial-soundtrack-family-computer-ios-linux-macos-ps4-gamerip-2016',
                'title': 'Drawful 2 Original Unofficial Soundtrack',
            },
            'playlist_mincount': 13,
        },
        {
            'url': 'https://downloads.khinsider.com/game-soundtracks/album/minecraft',
            'info_dict': {
                'id': 'minecraft',
                'title': 'Minecraft Soundtrack - Volume Alpha and Beta (Complete Edition)',
            },
            'playlist_mincount': 54,
        },
        {
            'url': 'https://downloads.khinsider.com/game-soundtracks/album/persona-5-royal-the-complete-soundtrack',
            'info_dict': {
                'id': 'persona-5-royal-the-complete-soundtrack',
                'title': 'Persona 5 Royal - The Complete Soundtrack',
            },
            'playlist_mincount': 140,
        }
    ]

    def _real_extract(self, url):
        album_id = self._match_id(url)
        webpage = self._download_webpage(url, album_id)
        
        # Extract album title
        title = self._html_search_regex(r'<h2>(.+?)</h2>', webpage, 'album title', default=None)
        if not title:
            title = album_id.replace('-', ' ').title()
        
        entries = []
        for song_path in re.findall(r'<a href="(/game-soundtracks/album/[^"]+)">(.+?)</a>', webpage):
            song_url = f'https://downloads.khinsider.com{song_path[0]}'
            song_title = clean_html(song_path[1])
            
            if song_title == 'get_app':
                # Stupid workaround for the get_app icon which also leads to the same download page
                # Probably would be a good idea to just remove duplicate links but that would require
                # to add an array that would store all the links but that would just be a waste of RAM
                # TODO: Find a better way to do this.
                continue
            
            try:
                song_page = self._download_webpage(song_url, album_id, note=f'Downloading page for {song_title}')
                mp3_url = self._html_search_regex(r'<audio.*?src="([^"]+)"', song_page, 'MP3 URL', default=None)
                sid = url.split('/')[-1]

                if not mp3_url:
                    self.report_warning(f'Could not find MP3 URL for {song_title}')
                    continue

                entries.append({
                    'id': sid,
                    'title': song_title,
                    'url': mp3_url,
                    'ext': 'mp3',
                })
            except ExtractorError as e:
                self.report_warning(f'Error extracting {song_title}: {e}')
                continue

        return self.playlist_result(entries, album_id, title)