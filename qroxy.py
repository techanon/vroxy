from __future__ import unicode_literals
import yt_dlp
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
# Need these to get low level url stuff.
from urllib.parse import urlparse, parse_qs


ydl_opts = {
    'format': 'best',
    'simulate': True,
    'forceurl': True
    }

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        print("test")
        query_components = parse_qs(urlparse(self.path).query)
        url = query_components["url"]
        print(url[0])
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info("{}".format(url[0]))
        self.send_response(301)
        self.send_header('Location',result['url'])
        self.end_headers()

    def do_HEAD(self):
        query_components = parse_qs(urlparse(self.path).query)
        url = query_components["url"]
        print(url[0])
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info("{}".format(url[0]))
        self.send_response(301)
        self.send_header('Location',result['url'])
        self.end_headers()
if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")