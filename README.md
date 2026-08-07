# YTDLP-KHInsider
A plugin that allows you to download MP3 and FLAC tracks from KHInsider via yt-dlp.

The extractor recognizes audio sources in `<audio>`/`<source>` elements as well as
direct MP3/FLAC download links. The output format is inferred from the source URL
or MIME type, so yt-dlp can apply the correct filename extension automatically.

## Installing
Run: <!-- wow, I really need a good readme --> <br>
```sh
pip install git+https://github.com/BurAndBY/ytdlp-khinsider.git
```

## Building
Just run `pip install -e .` and then do your edits.
After the edits don't forget to do Unit Testing.

## Unit Testing
`python .\setup.py test`
