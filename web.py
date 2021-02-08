import requests
from bs4 import BeautifulSoup
import browser_cookie3
import os
import re

from urllib import (
    parse
)

from debug import Debug

FIREFOX_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"

FILTER_SEARCH = [
    "imagevenue.com/", 
    "imagebam.com/", 
    "pixhost.to/",
    "lulzimg",
    "pimpandhost",
    "imagetwist",
    "imgbox",
    "turboimagehost"]

IMAGE_EXTS = (".jpg", ".bmp", ".jpeg", ".png", ".gif", ".tiff", ".ico")

_image_ext_pattern = re.compile("|".join(IMAGE_EXTS))

class Globals:
    regex_filter = None

def compile_regex_global_filter(filter_list=FILTER_SEARCH):
    Globals.regex_filter = re.compile("|".join(filter_list))

def is_valid_content_type(url, content_type, valid_types):
    """
    is_valid_content_type(str, str, dict)
    checks if mimetype is an image and matches valid images
    url           - the url of the content-type
    content_type  - is a string found in the headers['Content-Type'] dict
    valid_types   - a dict containing valid files for searching
    returns an empty string if not valid or a file extension related to the file type
    will always return a valid file extension if html document
    """
    ext = ""
    if 'text/html' in content_type:
        ext = ".html"
    elif content_type == 'image/gif' and valid_types["gif"]:
        ext = ".gif"
    elif content_type == 'image/png' and valid_types["png"]:
        ext = ".png"
    elif content_type == 'image/ico' and valid_types["ico"]:
        ext = ".ico"
    elif content_type == 'image/jpeg' and valid_types["jpg"]:
        ext = ".jpg"
    elif content_type == 'image/tiff' and valid_types["tiff"]:
        ext = ".tiff"
    elif content_type == 'image/tga' and valid_types["tga"]:
        ext = ".tga"
    elif content_type == 'image/bmp' and valid_types["bmp"]:
        ext = ".bmp"
    elif content_type == 'application/octet-stream':
        # file attachemnt use the extension from the url
        try:
            ext = os.path.splitext(url)[1]
        except IndexError as err:
            Debug.log("is_valid_content_type web.py", err, error=err.__str__(), url=url, content_type=content_type)
    return ext

def _appendlink(full_url, src, urllist):
    """
    _appendlink(str, str, list)
    joins the url to the src and then uses a filter pattern
    to search for matches. If a match is found then it is checked
    in the urllist for conflicts if none found then it appends
    to the urllist
    """
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

def get_title_from_html(html):
    soup = BeautifulSoup(html, features="html.parser")
    return soup.find("title")

def parse_html( url,
                html, 
                urls, 
                images_only=False, 
                thumbnails_only=False):
    """
    new_pasre_html(str, str, list, bool)
    takes in the url linked to the html document.
    the Urls is a reference ot the list all found links
    and images will be stored in it. Specify images_only
    if you only want to search for img and meta tags
    everything else will be ignored set to False by default.

    returns n size of found tags. 0 if none found
    """
    soup = BeautifulSoup(html, features="html.parser")

    if not images_only:
        # search for links on document
        atags = soup.find_all("a")
        for atag in atags:
            if thumbnails_only:
                if atag.find("img"):
                    _appendlink(url, atag.get("href"), urls)
            else:
                _appendlink(url, atag.get("href", ""), urls)
    
    # search image tags
    for imgtag in soup.find_all("img"):
        _appendlink(url, imgtag.get("src", ""), urls)

    # search images in meta data
    for metatag in soup.find_all("meta", content=_image_ext_pattern):
        _appendlink(url, metatag.get("content", ""), urls)
    
    return len(urls)

def _test():
    compile_regex_global_filter()
    cj = browser_cookie3.firefox()
    url = "http://vintage-erotica-forum.com/t18747-p90-milena-velba-cze.html"
    r = requests.get(url, cookies=cj)
    urls = []
    if parse_html(url, r.text, urls, False, True) > 0:
        for link in urls:
            print(link)
    r.close()

if __name__ == '__main__':
    _test()