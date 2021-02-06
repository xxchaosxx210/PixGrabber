import requests
from bs4 import BeautifulSoup
import browser_cookie3
import mimetypes

DEFAULT_USER_AGENT = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"

TEXT_HTML = "text/html"

def parse_html(html, thumbnail_only=True, level=1):
    """
    parser_html(str, int)
    if level 1 then return list of links and image tags found
    if level 2 then returns img only
    parsers html and looks for links and image tags
    """
    soup = BeautifulSoup(html)
    found_list = []
    if level == 1:
        anchors = soup.find_all("a")
        if thumbnail_only:
            for anchor in anchors:
                if anchor.find("img"):
                    found_list.append(anchor.get("href"))
        else:
            for anchor in anchors:
                found_list.append(anchor.href)
    else:
        imgs = soup.find_all("img")
        for img in imgs:
            found_list.append(img.get("src"))
    return found_list

def _test():
    print(parse_html(open("debug.html", "r").read()))

if __name__ == '__main__':
    _test()