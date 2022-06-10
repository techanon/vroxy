# Qroxy
Self-hosted light-weight server proxy for YoutubeDL.

Run with python3 and yt-dlp installed.

Currently in alpha.

Prep:
- Setup a public facing server (optionally with an associated domain name)
    It is _highly_ recommended to use a reverse proxy like NGINX to handle HTTPS frontloading of the server's public facing entry point and having that proxy the call to the _actual_ localhost endpoint
- Install python3 (make sure the `pip` tool is also installed)
- Get the latest copy of [ytdlp](https://github.com/yt-dlp/yt-dlp/releases/latest)
- Clone this repo to the server at your desired file path
- `cd` into the that file path in your desired command line
- Install the dependant packages for python via `python3 -m pip install -U yt-dlp aiohttp`
- Rename example.ini to settings.ini and change the settings as you need

Usage:
Run the server via `python3 /path/to/repo/qroxy.py`
Then access the url via `https://mydomainorip/?url=https://youtube.com/watch?v=VIDEO_ID` to receive a 307 redirect to the direct link video url.

Optional parameters:
- `f`: Specific format id for the given url that is desired. This is something that is looked up ahead of time via manually checking --list-formats in ytdl.
- `s`: Custom sort order for ytdl to determine what it thinks is 'best'. Sort order options can be found [Here](https://github.com/yt-dlp/yt-dlp/blob/release/README.md#sorting-formats)
- `m`: Specific presets for sort order options
    - `0` - aka "hasvid,hasaud,res:1440" for decent sized media with audio+video, generally compatible with all platforms
    - `1` - aka "hasvid,hasaud,res" for sort preferring audio+video with the highest quality
    - `2` - aka "hasvid,hasaud,+res" for sort preferring audio+video with the lowest quality
    - `3` - aka "hasvid,res,codec:vp9" for sort preferring highest quality with priority on VP9 codec for platform compatibility
    - `4` - aka "hasvid,res" for sort preferring highest quality without concern for codec or audio
