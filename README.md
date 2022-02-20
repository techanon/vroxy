# qroxy
Self-hosted light-weight server proxy for YoutubeDL.

Run with python3 and yt-dlp (or your preferred fork of youtubeDL) installed.

Currently in alpha pending next release with early caching.

Prep:
- Setup a public facing server (optionally with an associated domain name)
    It is _highly_ recommended to use a reverse proxy like NGINX to handle HTTPS frontloading of the server's public facing entry point and having that proxy the call to the _actual_ localhost endpoint
- Install python3 with pip
- Get the latest copy of [ytdlp](https://github.com/yt-dlp/yt-dlp/releases/latest)
- Clone this repo to the server at your desired file path
- `cd` into the that file path in your desired command line
- Install the dependant packages for python via `pip install yt_dlp aiohttp`
- Rename example.ini to settings.ini and change the settings as you need

Usage:
Run the server via `python3 /path/to/repo/qroxy.py`
Then access the url via `https://mydomainorip/?url=https://youtube.com/watch?v=VIDEO_ID` to receive a 301 redirect to the direct link video url.