# Checks the source and prompts for a re-download

import requests
import re
from bs4 import BeautifulSoup
from zipfile import ZipFile
import os
import shutil
import sys
import time
import datetime


def get_file_links(url_in):
    # This function gets a list of the links on the page and distill into zips and sgfs
    req = requests.get(url_in, allow_redirects=True)
    soup = BeautifulSoup(req.text, "html.parser")
    links = soup.find_all("a")

    zips = []  # Collect .zip files
    sgfs = []  # Collect .sgf files (native)
    expansion = []  # A spot for sub-directories, allows recursion

    for link in links:
        href_code = link.get("href")  # Get the href
        # First, filter out errors
        if len(href_code) == 0:
            pass
        elif href_code == None:
            pass
        # If there are zips or sgfs in the directory...
        elif href_code.endswith(".zip"):
            zips.append(url_in + href_code)
        elif href_code.endswith(".sgf"):
            sgfs.append(url_in + href_code)
        # Finally, if there are any other valid directories to search...
        elif href_code.startswith("archive") or href_code.startswith("games"):
            expansion.append(href_code)

    for url in expansion:
        # For each url, conduct the same method...
        new_url = url_in + url
        print("Reading sub-directory " + new_url)
        new_zips, new_sgfs, new_expansion = get_file_links(new_url)  # Recursively run the function
        zips.extend(new_zips)
        sgfs.extend(new_sgfs)

    return zips, sgfs, expansion


def downloader(url, dl_path, extract_path, full_download=False):
    # Prepare the file for manipulation
    file_ext = url[-4:]
    str_split = url.split('/')
    filename = str_split[-1]

    if os.path.isfile(dl_path + "/" + filename) and not full_download:
        print("Skipping download of " + filename)  # Mechanism to skip downloads
        return None
    else:
        print("Downloading " + filename)
        with open(dl_path + filename, "wb") as f:
            req = requests.get(url, stream=True)
            total_length = req.headers.get("content-length")

            if total_length is None:
                f.write(req.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in req.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl/total_length)
                    sys.stdout.write("\r[%s%s]" % ("=" * done, " " * (50-done)))
                    sys.stdout.flush()
        #print("\rPausing for 0.01 second...\n")
        #time.sleep(0.01)  # Force a 0.1 second delay to not kill the website

    if file_ext == ".zip":

        file_date = re.findall("[A-Z][a-z]{2}-.+-\d{4}", filename)
        file_mon = file_date[0][0:3]

        # Convert month to numeric
        mon_dict = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12"
        }
        file_full = file_date[0][-4:] + "-" + mon_dict[file_mon] + "/"

    elif file_ext == ".sgf":
        file_date = re.findall("-\d{4}-\d{2}-\d{2}-\d{4}", filename)
        file_full = file_date[0][1:8] + "/"

    if not os.path.isdir(extract_path + file_full):
        os.mkdir(extract_path + file_full)

    if file_ext == ".sgf":
        print("\rCopying " + filename)
        shutil.copy(dl_path + filename, extract_path + file_full)
    elif file_ext == ".zip":
        print("\rUnzipping " + filename)
        with ZipFile(dl_path + filename, "r") as zipObj:
            zipObj.extractall(extract_path + file_full)
    return None


# Script test to be commented
start_time = datetime.datetime.now()

import_url = "http://www.boardspace.net/hive/hivegames/"
zips, sgfs, expansion = get_file_links(import_url)

download_list = sgfs + zips
download_path = "../data/download_raw/"
game_path = "../data/download_games/"


for download_req in download_list:
    downloader(download_req, download_path, game_path)

end_time = datetime.datetime.now()
time_taken = end_time - start_time
print("Execution time: {}s".format(time_taken))
