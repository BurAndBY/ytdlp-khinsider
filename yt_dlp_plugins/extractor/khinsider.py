#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import html
import re
from urllib.parse import urljoin, urlparse

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import ExtractorError, clean_html, determine_ext, unescapeHTML


class _KHInsiderBaseIE(InfoExtractor):
    _BASE_URL = 'https://downloads.khinsider.com'

    def _media_formats(self, webpage, page_url):
        """Find all usable audio sources, regardless of markup or format."""
        candidates = []
        # Audio and source tags may put src before or after type, and use either quote style.
        for tag in re.findall(r'<(?:audio|source)\b[^>]*>', webpage, flags=re.I):
            attrs = dict((key.lower(), html.unescape(value)) for key, value in re.findall(
                r'''([\w:-]+)\s*=\s*["']([^"']+)["']''', tag, flags=re.I))
            if attrs.get('src'):
                candidates.append((attrs['src'], attrs.get('type')))
        # Some pages expose a direct download link without an audio element.
        for value in re.findall(r'''<a\b[^>]+href\s*=\s*["']([^"']+\.(?:mp3|flac)(?:\?[^"']*)?)["']''', webpage, flags=re.I):
            candidates.append((html.unescape(value), None))
        formats, seen = [], set()
        for source, mime in candidates:
            source = urljoin(page_url, unescapeHTML(source))
            ext = determine_ext(source) or ((mime or '').split('/')[-1].lower() if mime else None)
            if ext in ('mp3', 'flac') and source not in seen:
                seen.add(source)
                formats.append({
                    'url': source,
                    'ext': ext,
                    'format_id': ext,
                    'vcodec': 'none',
                    'quality': 1 if ext == 'flac' else 0,
                })
        return formats

    def _title(self, webpage, fallback):
        title = self._html_search_regex(
            (r'<meta\s+[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)',
             r'<h2\b[^>]*>(.*?)</h2>', r'<title\b[^>]*>(.*?)</title>'),
            webpage, 'title', default=None, fatal=False)
        return clean_html(title).strip() if title else fallback


class KHInsiderTrackIE(_KHInsiderBaseIE):
    __version__ = '0.2.0'
    _WORKING = True
    IE_NAME = 'khinsider_track'
    IE_DESC = "Bur's KHInsider VGM Downloader [MP3 and FLAC]"
    IE_BUG_REPORT = 'Please report this issue on https://github.com/burandby/bursytdlps'
    _VALID_URL = r'https?://downloads\.khinsider\.com/game-soundtracks/album/[^/]+/(?P<id>[^/?#]+)'

    def _real_extract(self, url):
        track_id = self._match_id(url)
        webpage = self._download_webpage(url, track_id)
        title = self._html_search_regex(r'Song\s+name\s*:\s*</?[^>]*>\s*([^<\r\n]+)', webpage,
                                        'song title', default=None, fatal=False)
        title = clean_html(title).strip() if title else clean_html(track_id.rsplit('.', 1)[0]).strip()
        formats = self._media_formats(webpage, url)
        if not formats:
            raise ExtractorError('Could not find an MP3 or FLAC URL')
        return {'id': track_id, 'title': title, 'formats': formats}


class KhinsiderAlbumIE(_KHInsiderBaseIE):
    __version__ = '0.2.0'
    _WORKING = True
    IE_NAME = 'khinsider:album'
    IE_DESC = "Bur's KHInsider VGM Downloader [MP3 and FLAC]"
    IE_BUG_REPORT = 'Please report this issue on https://github.com/burandby/bursytdlps'
    _VALID_URL = r'https?://downloads\.khinsider\.com/game-soundtracks/album/(?P<id>[\w-]+)'

    def _real_extract(self, url):
        album_id = self._match_id(url)
        webpage = self._download_webpage(url, album_id)
        title = self._title(webpage, album_id.replace('-', ' ').title())
        songlist = self._search_regex(
            r'<table\b[^>]*\bid=["\']songlist["\'][^>]*>(.*?)</table>',
            webpage, 'song list', flags=re.I | re.S)
        entries, seen = [], set()
        for path, raw_title in re.findall(r'<a\b[^>]*href=["\'](/game-soundtracks/album/[^"\']+)["\'][^>]*>(.*?)</a>', songlist, re.I | re.S):
            song_url = urljoin(self._BASE_URL, path)
            song_id = urlparse(song_url).path.rsplit('/', 1)[-1]
            # Album navigation contains a self-link (currently labelled "Change Log").
            if song_id == album_id or song_id in seen or song_id.lower() == 'get_app':
                continue
            seen.add(song_id)
            song_title = clean_html(raw_title).strip()
            try:
                song_page = self._download_webpage(song_url, album_id, note=f'Downloading page for {song_title}')
                formats = self._media_formats(song_page, song_url)
                if not formats:
                    self.report_warning(f'Could not find MP3 or FLAC URL for {song_title}')
                    continue
                entries.append({'id': song_id, 'title': song_title or song_id, 'formats': formats})
            except ExtractorError as err:
                self.report_warning(f'Error extracting {song_title}: {err}')
        return self.playlist_result(entries, album_id, title)
