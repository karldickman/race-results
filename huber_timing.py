#!/usr/bin/env python
from operator import itemgetter
from os import mkdir, path

from bs4 import BeautifulSoup
from pandas import concat, DataFrame
import pdfkit
import requests

DOWNLOADS = "download-cache"
FACSIMILES = "facsimiles"
OUT = "out"

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

def download_race_results(url: str) -> str:
    save_facsimile(url)
    return fetch(url)

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

def parse(url: str, content: str) -> tuple[DataFrame, DataFrame]:
    soup = BeautifulSoup(content, features = "lxml")
    # Race results
    table = soup.find(id = "individualResults")
    if table is None:
        raise Exception("Error: could not find #individualResults table")
    table_head = table.find("thead")
    columns = table_head.find_all("th")
    columns = [column.text.strip() for column in columns]
    data: dict[str, list[str]] = dict(zip(columns, [[] for _ in columns]))
    table_body = table.find("tbody")
    rows = list(table_body.find_all("tr"))
    for row in rows:
        cells = row.find_all("td")
        cells = [cell.text.strip() for cell in cells]
        for column, cell in zip(columns, cells):
            data[column].append(cell)
    # Race metadata
    metadata_strings = tuple(soup.find("big").stripped_strings)
    name = metadata_strings[0]
    location = metadata_strings[1]
    date = metadata_strings[2]
    host = metadata_strings[3] if len(metadata_strings) > 3 else None
    data["Race"] = [name for _ in rows]
    metadata = DataFrame(data = {
        "Race": [name],
        "Location": [location],
        "Date": [date],
        "Host": [host],
        "URL": [url],
    })
    results = DataFrame(data = data)
    return metadata, results

if __name__ == "__main__":
    for dir in [DOWNLOADS, FACSIMILES, OUT]:
        if not path.exists(dir):
            mkdir(dir)
    with open("huber_timing.txt", "r") as url_file:
        urls = [url.strip() for url in url_file.readlines()]
    race_results = [parse(url, download_race_results(url)) for url in urls]
    all_races = concat(map(itemgetter(0), race_results))
    all_race_results = concat(map(itemgetter(1), race_results)).loc[:, [
        "Place",
        "Bib",
        "Name",
        "Gender",
        "Age",
        "City",
        "State",
        "Time to Start",
        "Gun Time",
        "Time",
        "Distance"
    ]]
    all_people = all_race_results[["Name", "Gender"]] \
        .drop_duplicates(subset = ["Name", "Gender"]) \
        .sort_values(by = ["Name"])
    # Write results
    all_races.to_csv(path.join(OUT, "huber_timing_races.csv"))
    all_race_results.to_csv(path.join(OUT, "huber_timing_results.csv"))
    all_people.to_csv(path.join(OUT, "huber_timing_people.csv"))
    print(all_races)