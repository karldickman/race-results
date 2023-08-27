#!/usr/bin/env python

from itertools import chain
import json
from os import path

from pandas import concat, DataFrame

from directories import OUT
from download import fetch

def flatten(list_of_lists: list[list]) -> list:
    return list(chain.from_iterable(list_of_lists))

def download_race_results(url: str):
    page = 1
    while page <= 80:
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
    if page >= 80:
        print(f"Stopped loading {url} at 80 pages")

def fetch_race_urls(slug: str):
    response = json.loads(fetch(f"https://api.enmotive.grepcv.com/prod/events/{slug}", "json"))
    if response["error"] != {}:
        print("Error retrieving URLs for", slug)
        return
    race_metadata = json.loads(response["body"])
    if race_metadata["leaderboards"] == []:
        print("Error retrieving URLs for", slug)
        return
    for category in race_metadata["leaderboards"]["categories"]:
        for bracket in category["brackets"]:
            if bracket["name"] != "Overall":
                continue
            url = race_url(race_metadata["id"], bracket["id"])
            yield url

def race_url(event_id: str, race_id: str) -> str:
    return f"https://api.enmotive.grepcv.com/prod/events/{event_id}/leaderboards?bracket_id={race_id}"

def results_to_data_frame(url: str, results: list[dict]) -> DataFrame:
    columns = set(flatten(map(lambda entry: list(entry.keys()), results)))
    data = dict(zip(columns, [[] for _ in columns]))
    data["url"] = []
    for entry in results:
        for column in entry:
            data[column].append(entry[column])
        data["url"].append(url)
    return DataFrame(data = data)

def main(slugs_file_path: str) -> None:
    with open(slugs_file_path, "r") as slug_file:
        slugs = [slug.strip() for slug in slug_file.readlines()]
    urls = flatten(map(fetch_race_urls, slugs))
    data_frame_each_race = []
    for url in urls:
        race_results = list(download_race_results(url))
        race_results_data_frame = results_to_data_frame(url, race_results)
        data_frame_each_race.append(race_results_data_frame)
    all_races = concat(data_frame_each_race)
    all_races.to_csv(path.join(OUT, "enmotive_results.csv"))
    print(all_races)

if __name__ == "__main__":
    main("enmotive.txt")