import requests
from bs4 import BeautifulSoup
import browser_cookie3
import mimetypes

DEFAULT_USER_AGENT = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"

TEXT_HTML = "text/html"

def parse_html(thumbnail_only):
    pass

def _test():
    url = "http://vintage-erotica-forum.com/t18747-p87-milena-velba-cze.html"
    r = requests.get(url, DEFAULT_USER_AGENT)
    if TEXT_HTML in r.headers["Content-Type"]:
        text = r.text
        bs = BeautifulSoup(text)
        links = bs.find_all("a")
        for link in links:
            print(link)

if __name__ == '__main__':
    _test()