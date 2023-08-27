#!/usr/bin/env python
from operator import itemgetter
from os import path

from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date
from pandas import concat, DataFrame

from directories import OUT
from download import download_race_results

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

def parse(url: str, content: str) -> tuple[dict[str, str | None], DataFrame]:
    soup = BeautifulSoup(content, features = "lxml")
    # Race results
    table = soup.find(id = "individualResults")
    if table is None:
        raise Exception("Error: could not find #individualResults table")
    table_head = table.find("thead")
    columns = table_head.find_all("th")
    columns = [column.text.strip() for column in columns]
    data: dict[str, list[str]] = dict(zip(columns, [[] for _ in columns]))
    data["URL"] = []
    table_body = table.find("tbody")
    rows = list(table_body.find_all("tr"))
    for row in rows:
        cells = row.find_all("td")
        cells = [cell.text.strip() for cell in cells]
        for column, cell in zip(columns, cells):
            data[column].append(cell)
        data["URL"].append(url)
    # Race metadata
    metadata_strings = tuple(soup.find("big").stripped_strings)
    name = metadata_strings[0]
    location = metadata_strings[1]
    date_strings = list(map(lambda string: string.strip(), metadata_strings[2].split("-")))
    host = metadata_strings[3] if len(metadata_strings) > 3 else None
    data["Race"] = [name for _ in rows]
    metadata = {
        "Race": name,
        "Location": location,
        "Date": parse_date(date_strings[0]),
        "End Date": parse_date(date_strings[1]) if len(date_strings) > 1 else None,
        "Host": host,
        "URL": url,
    }
    results = DataFrame(data = data)
    return metadata, results

if __name__ == "__main__":
    with open("huber_timing.txt", "r") as url_file:
        urls = [url.strip() for url in url_file.readlines()]
    race_results = [parse(url, download_race_results(url)) for url in urls]
    race_results = [(race, results) for (race, results) in race_results if race["Location"] != "Virtual"]
    all_races_data = {
        "Race": [],
        "Location": [],
        "Date": [],
        "Host": [],
        "URL": [],
    }
    for race_metadata, _ in race_results:
        for property in all_races_data:
            all_races_data[property].append(race_metadata[property])
    all_races = DataFrame(data = all_races_data)
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
        "Distance",
        "URL",
    ]]
    all_people = all_race_results[["Name"]] \
        .drop_duplicates(subset = ["Name"]) \
        .sort_values(by = ["Name"])
    # Write results
    all_races.to_csv(path.join(OUT, "huber_timing_races.csv"))
    all_race_results.to_csv(path.join(OUT, "huber_timing_results.csv"))
    all_people.to_csv(path.join(OUT, "huber_timing_people.csv"))
    print(all_races)