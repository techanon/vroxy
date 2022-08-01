# Vroxy
Self-hosted light-weight server proxy for YoutubeDL, originally designed for use in VRChat.

Currently in alpha.

Prerequisites:
- Ensure you have a VPS or better with a linux OS on it (debian is recommended). You will need to be able to run commands with escalated privilege.
- Ensure you have a domain name setup correctly with the desired DNS A entry pointing to your server's public IP address.

Debian/Ubuntu Setup:
- Pull the repo's install script and run it:  
    - `wget -q https://raw.githubusercontent.com/techanon/vroxy/master/vroxy_install_deb.sh -O vroxy_install.sh && sudo bash ./vroxy_install.sh`
    - This will pull in all dependencies and setup the nginx reverse proxy and SSL certs for you.
    - The script will use `/var/vroxy` as the install folder by default, but you can specify another location if you wish.
    - If running on an OS without the sudo command, you will either need to login as root `su -` or install sudo and add yourself as a sudo user.
- Run the reload script to update and (re)start the service: `bash /var/vroxy/vroxy_reload.sh`
- You can examine the service log with: `tmux a -t vroxy`
- Exit tmux with `CTRL+B` followed by the `D` key.

Generic Setup:
- Setup a public facing server on your VPS or whatever.
    - This requires something like Apache or Nginx and some SSL cert assigned (using LetsEncrypt's certbot tool is the recommended option)
    - Quest _requires_ HTTPS, so the SSL cert is a must.
- Install python3 (make sure the `pip` tool is also installed)
- Clone this repo to the server at your desired file path. `/var/vroxy` is recommended.
- Navigate your terminal to the given folder that Vroxy was cloned into.
- Install the dependant packages for python via `python3 -m pip install -U yt-dlp aiohttp`
- Copy example.ini to settings.ini and change the settings as you need
- Run the server via `python3 /path/to/repo/vroxy.py`
    - You may want to consider a terminal multiplexer (like tmux) to run the service without needing to be connected to the terminal.

Usage:
Access the url via `https://mydomain/?url=https://youtube.com/watch?v=VIDEO_ID` to receive a 307 redirect to the direct link video url.

Optional parameters:
- `f`: Specific format id for the given url that is desired. This is something that is looked up ahead of time via manually checking --list-formats in ytdl.
- `s`: Custom sort order for ytdl to determine what it thinks is 'best'. Sort order options can be found [Here](https://github.com/yt-dlp/yt-dlp/blob/release/README.md#sorting-formats)
- `m`: Specific presets for sort order options
    - `0` - aka "hasvid,hasaud,res:1440" for decent sized media with audio+video, generally compatible with all platforms
    - `1` - aka "hasvid,hasaud,res" for sort preferring audio+video with the highest quality
    - `2` - aka "hasvid,hasaud,+res" for sort preferring audio+video with the lowest quality
    - `3` - aka "hasvid,res,codec:vp9" for sort preferring highest quality with priority on VP9 codec for platform compatibility
    - `4` - aka "hasvid,res" for sort preferring highest quality without concern for codec or audio


TODO: Add discord embed support ala https://github.com/robinuniverse/TwitFix/blob/main/templates/index.html because why not?

## Docker deployment

<!-- TODO: sub frizzle-chan container for official one -->
In general you can deploy `ghcr.io/frizzle-chan/vroxy:dev` to any platform that supports running docker containers.

### VPS

On a bare VPS with [Docker][docker-install] and [docker-compose][docker-compose-install] installed:
1. Clone the repo
2. Copy example.ini to setup.ini and fill in the proper values
3. ```sh
   docker-compose up -d
   ```

### Google Cloud Platform: [Cloud Run](https://cloud.google.com/run)

1. Push your docker container to [Google Cloud Registry](https://cloud.google.com/container-registry) or use the official one: <tbd>
2. All the default settings should just work. But you might want to take care to look at the following settings:
  - Set maximum replicas to 1
  - Allow all traffic
  - Allow unauthenticated invocations
3. After a short initialization time, you should have a public service up and running

## Docker development

- Ensure you [have Docker installed][docker-install].
- [Install docker-compose][docker-compose-install]
- [Install make](https://command-not-found.com/make)

Using make is optional if you already know how to use docker-compose.

To build the docker containers:

```sh
make
```

Run the tests:

```sh
make test
```

To launch a shell inside the dev container:

```sh
make sh
```

To run the local development server:

```
docker-compose up
```

[docker-install]: https://docs.docker.com/engine/install/
[docker-compose-install]: https://docs.docker.com/compose/install/
