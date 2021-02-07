import requests
from bs4 import BeautifulSoup
import browser_cookie3
import os
import re
from urllib import (
    parse
)

from debug import Debug

DEFAULT_USER_AGENT = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"

TEXT_HTML = "text/html"

FILTER_SEARCH = ["imagevenue.com/", "imagebam.com/", "pixhost.to/"]

_image_ext_pattern = re.compile('.jpg|.png|.tiff|.gif|.bmp|.jpeg')

class Globals:
    regex_filter = None

def compile_regex_global_filter(filter_list=FILTER_SEARCH):
    Globals.regex_filter = re.compile("|".join(filter_list))

def is_valid_content_type(url, content_type, valid_types):
    """
    is_valid_content_type(str, str, list)
    checks if mimetype is an image and matches valid images
    url           - the url of the content-type
    content_type  - is a string found in the headers['Content-Type'] dict
    valid_types   - a list containing valid files for searching
    returns an empty string if not valid or a file extension related to the file type
    will always return a valid file extension if html document
    """
    ext = ""
    if 'text/html' in content_type:
        ext = ".html"
    elif content_type == 'image/gif':
        ext = ".gif"
    elif content_type == 'image/png':
        ext = ".png"
    elif content_type == 'image/ico':
        ext = ".ico"
    elif content_type == 'image/jpeg':
        ext = ".jpg"
    elif content_type == 'image/tiff':
        ext = ".tiff"
    elif content_type == 'image/tga':
        ext = ".tga"
    elif content_type == 'image/bmp':
        ext = ".bmp"
    elif content_type == 'application/octet-stream':
        # file attachemnt use the extension from the url
        try:
            ext = os.path.splitext(url)[1]
        except IndexError as err:
            Debug.log(f"is_valid_content_type web.py", err, error=err.__str__(), url=url, content_type=content_type)
    return ext

def _appendlink(full_url, src, urllist):
    if src:
        url = parse.urljoin(full_url, src)
        # Filter the URL
        if Globals.regex_filter.search(url):
            # make sure we dont have a duplicate
            # exception ValueError raised if no url found so add it to list
            try:
                urllist.index(url)
            except ValueError:
                urllist.append(url)

def parse_html(url, html, thumbnail_only=True, level=1):
    """
    parser_html(str, int)
    if level 1 then return list of links and image tags found
    if level 2 then returns img only
    parsers html and looks for links and image tags
    """
    soup = BeautifulSoup(html, features="html.parser")
    found_list = []
    if level == 1:
        anchors = soup.find_all("a")
        if thumbnail_only:
            for anchor in anchors:
                if anchor.find("img"):
                    # add the href from the anchor we dont want the thumbnail image
                    _appendlink(url, anchor.get("href"), found_list)
        else:
            for anchor in anchors:
                _appendlink(url, anchor.get("href"), found_list)
    else:
        # second level; scan img tags only
        imgs = soup.find_all("img")
        for img in imgs:
            _appendlink(url, img.get("src"), found_list)
        # find the meta data
        for meta in soup.find_all("meta", content=_image_ext_pattern):
            _appendlink(url, meta.get("content"), found_list)
    return found_list

def _test():
    compile_regex_global_filter()
    cj = browser_cookie3.firefox()
    url = "http://www.imagebam.com/image/7382191329586630"
    r = requests.get(url, cookies=cj)
    print(parse_html(url, r.text, True, 2))
    r.close()
    # print(is_valid_content_type(url, r.headers["Content-Type"], None))
    # import time
    # for x in range(10, 0, -1):
    #     print(f"File will download in less than {x} minutes")
    #     time.sleep(60)
    # fp = open("cat.png", "wb")
    # for buff in r.iter_content(1000):
    #     fp.write(buff)
    # print("Done")
    r.close()

if __name__ == '__main__':
    _test()