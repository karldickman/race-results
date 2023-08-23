#!/usr/bin/env python
from os import mkdir, path

from bs4 import BeautifulSoup
from pandas import DataFrame
import pdfkit
import requests

DOWNLOADS = "download-cache"
FACSIMILES = "facsimiles"

def safe_file_name(url: str, extension: str) -> str:
    file_name = url
    for chr in ["<", ">", ":", "\"", "/", "\\", "|", "?"]:
        file_name = file_name.replace(chr, "_")
    return file_name + "." + extension

def fetch(url: str) -> str:
    cached_file_name = safe_file_name(url, "html")
    cached_file_path = path.join(DOWNLOADS, cached_file_name)
    if path.isfile(cached_file_path):
        with open(cached_file_path, "r") as cached_file:
            return cached_file.read()
    result = requests.get(url)
    content = result.text
    with open(cached_file_path, "w") as cached_file:
        cached_file.write(content)
    return content

def save_facsimile(url: str) -> None:
    file_name = safe_file_name(url, "pdf")
    facsimile_path = path.join(FACSIMILES, file_name)
    if not path.isfile(facsimile_path):
        pdfkit.from_url(url, facsimile_path, { "orientation": "Landscape" })

def get_linked_results(content: str) -> list[str]:
    soup = BeautifulSoup(content, features = "lxml")
    navigation_containers = soup.find_all("div", { "class": "text-center" })
    for navigation_container in navigation_containers:
        buttons = navigation_container.find_all("a", { "role": "button" })
        for button in buttons:
            href: str = button["href"]
            if any(map(lambda frag: href.startswith(f"/results/{frag}"), ["2016", "feed", "gallery", "team", "summary"])):
                continue
            if "virtual" in href.lower() or "walk" in href.lower():
                continue
            yield "https://www.hubertiming.com" + button["href"]

def parse(content: str) -> DataFrame:
    soup = BeautifulSoup(content, features = "lxml")
    table = soup.find(id = "individualResults")
    if table is None:
        print("Error: could not find #individualResults table")
        return
    table_head = table.find("thead")
    columns = table_head.find_all("th")
    columns = [column.text.strip() for column in columns]
    data: dict[str, list[str]] = dict(zip(columns, [[] for _ in columns]))
    table_body = table.find("tbody")
    rows = table_body.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        cells = [cell.text.strip() for cell in cells]
        for column, cell in zip(columns, cells):
            data[column].append(cell)
    return DataFrame(data = data)

if __name__ == "__main__":
    if not path.exists(DOWNLOADS):
        mkdir(DOWNLOADS)
    if not path.exists(FACSIMILES):
        mkdir(FACSIMILES)
    with open("huber_timing.txt", "r") as url_file:
        urls = [url.strip() for url in url_file.readlines()]
    for url in urls:
        save_facsimile(url)
        content = fetch(url)
        data = parse(content)
        print(url)
        if not data is None:
            print(data)
        #for linked_url in get_linked_results(content):
        #    print(linked_url)