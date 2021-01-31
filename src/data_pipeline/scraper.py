# Checks the source and prompts for a re-download

import requests
import re
from bs4 import BeautifulSoup

import_url = "http://www.boardspace.net/hive/hivegames/"


def get_file_links(url_in):
    # This function gets a list of the links on the page and distill into zips and sgfs
    req = requests.get(url_in, allow_redirects=True)
    soup = BeautifulSoup(req.text, "html.parser")
    links = soup.find_all("a")

    zips = []
    sgfs = []
    expansion = []

    for link in links:
        href_code = link.get("href")  # Get the href
        # First, filter out errors
        if len(href_code) == 0:
            pass
        elif href_code == None:
            pass
        # If there are zips or sgfs in the directory...
        elif href_code.endswith(".zip"):
            zips.append(url_in + link)
        elif href_code.endswith(".sgf"):
            sgfs.append(url_in + link)
        # Finally, if there are any other valid directories to search...
        elif href_code.startswith("archive") or href_code.startswith("games"):
            expansion.append(href_code)

    for url in expansion:
        # For each url, conduct the same method...
        new_url = url_in + url
        print("Conducting recursion on " + new_url)
        new_zips, new_sgfs, new_expansion = get_file_links(new_url)
        zips.extend(new_zips)
        sgfs.extend(new_sgfs)

    return zips, sgfs, expansion


#def downloader(url):
#    # ADD EXISTENCE CHECK



zips, sgfs, expansion = get_file_links(import_url)

print(zips)




#def get_fn(dir):
#    if not dir:
#        return None
#    fname = re.findall("filename=(.+)", dir)
#    if len(fname) == 0:
#        return None
#    return fname[0]
#
#import_url = "http://www.boardspace.net/hive/hivegames/"
#download_path = "../data/"
#
#req = requests.get(import_url, allow_redirects=True)
#filename = download_path
#with open(filename, "wb") as f:
#    f.write(req.content)