#!/usr/bin/env python

from itertools import chain
import json
from os import path

from pandas import concat, DataFrame

from directories import OUT
from download import fetch

def flatten(list_of_lists: list[list]) -> list:
    return list(chain.from_iterable(list_of_lists))

def download_race_results(url):
    page = 1
    while True:
        results = json.loads(fetch(f"{url}&page={page}", "json"))
        body = json.loads(results["body"])
        if len(body) == 0:
            break
        for category in body["categories"]:
            for bracket in category["brackets"]:
                if bracket["name"] != "Overall":
                    continue
                for entry in bracket["leaders"]:
                    entry["category"] = category["name"]
                    yield entry
        page += 1

def results_to_data_frame(url: str, results: list[dict]) -> DataFrame:
    columns = set(flatten(map(lambda entry: list(entry.keys()), results)))
    data = dict(zip(columns, [[] for _ in columns]))
    data["url"] = []
    for entry in results:
        for column in entry:
            data[column].append(entry[column])
        data["url"].append(url)
    return DataFrame(data = data)

def main(urls_file_path: str) -> None:
    with open(urls_file_path, "r") as url_file:
        urls = [url.strip() for url in url_file.readlines()]
    data_frame_each_race = []
    for url in urls:
        race_results = list(download_race_results(url))
        race_resutls_data_frame = results_to_data_frame(url, race_results)
        data_frame_each_race.append(race_resutls_data_frame)
    all_races = concat(data_frame_each_race)
    all_races.to_csv(path.join(OUT, "enmotive_results.csv"))
    print(all_races)

if __name__ == "__main__":
    main("enmotive.txt")