#!/usr/bin/env python

from os import path

from pandas import concat, read_csv

from directories import OUT

def main():
    # Races
    huber_races = read_csv(path.join(OUT, "huber_timing_races.csv"))
    enmotive_races = read_csv(path.join(OUT, "enmotive_races.csv"))
    huber_races = huber_races.rename(columns = {
        "Race": "race",
        "Location": "venue",
        "Date": "date",
        "Host": "host",
        "URL": "url",
    })
    huber_races["provider"] = "Huber Timing"
    enmotive_races["provider"] = "Enmotive"
    races = concat([huber_races, enmotive_races])
    # Results
    huber_results = read_csv(path.join(OUT, "huber_timing_results.csv"))
    enmotive_results = read_csv(path.join(OUT, "enmotive_results.csv"))
    huber_results = huber_results.rename(columns = {
        "Place": "place",
        "Bib": "bib",
        "Name": "name",
        "City": "hometown",
        "URL": "url",
        "Time": "time",
    })
    enmotive_results = enmotive_results.drop(columns=["registration_id", "pace", "pace_unit"])
    enmotive_results = enmotive_results.rename(columns = {
        "rank": "place",
    })
    huber_results["provider"] = "Huber Timing"
    enmotive_results["provider"] = "Enmotive"
    results = concat([huber_results, enmotive_results])
    # People
    huber_people = read_csv(path.join(OUT, "huber_timing_people.csv"))
    enmotive_people = read_csv(path.join(OUT, "enmotive_people.csv"))
    huber_people = huber_people.rename(columns = { "Name": "name" })
    people = concat([huber_people, enmotive_people])
    people = people[["name"]] \
        .drop_duplicates(subset = ["name"]) \
        .sort_values(by = ["name"])
    # Write combined data
    races.to_csv(path.join(OUT, "races.csv"))
    results.to_csv(path.join(OUT, "results.csv"))
    people.to_csv(path.join(OUT, "people.csv"))
    print(results)

if __name__ == "__main__":
    main()