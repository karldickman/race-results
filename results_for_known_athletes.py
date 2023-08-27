#!/usr/bin/env python

from os import path

from pandas import isnull, read_csv

from directories import IN, OUT

def main():
    # Associate athlete names with their club memberships
    names = read_csv(path.join(IN, "canonical_names.csv"))
    affiliations = read_csv(path.join(IN, "affiliations.csv"), parse_dates = ["from", "to"], dtype = {
        "athlete": "string",
        "team": "string",
        "notes": "string",
    })
    athletes = names \
        .set_index("athlete") \
        .join(affiliations.set_index("athlete")) \
        .reset_index() \
        .loc[:, [
            "athlete",
            "name",
            "from",
            "to",
            "notes",
        ]]
    # Associate known athletes with results
    results = read_csv(path.join(OUT, "results.csv"), dtype = {
        "place": "float",
        "bib": "string",
        "name": "string",
        "Gender": "string",
        "Age": "float",
        "hometown": "string",
        "State": "string",
        "Time to Start": "string",
        "Gun Time": "string",
        "time": "string",
        "Distance": "string",
        "url": "string",
        "provider": "string",
        "category": "string",
    })
    known_athlete_results = athletes \
        .set_index("name") \
        .join(results.set_index("name")) \
        .reset_index() \
        .loc[:, [
            "athlete",
            "hometown",
            "from",
            "to",
            "notes",
            "Gender",
            "Age",
            "Time to Start",
            "Gun Time",
            "time",
            "url",
        ]]
    # Associate results with race metadata
    races = read_csv(path.join(OUT, "races.csv"), parse_dates = ["date"], dtype = {
        "race": "string",
        "venue": "string",
        "host": "string",
        "url": "string",
    })
    known_athlete_results = known_athlete_results \
        .set_index("url") \
        .join(races.set_index("url")) \
        .reset_index()
    # Tag whether they were members of the team
    known_athlete_results["team_member"] = (known_athlete_results["from"] <= known_athlete_results["date"]) \
        & ((known_athlete_results["to"] >= known_athlete_results["date"]) \
           | (isnull(known_athlete_results["to"])))
    known_athlete_results = known_athlete_results.loc[:, [
        "athlete",
        "hometown",
        "notes",
        "team_member",
        "Gender",
        "Age",
        "Time to Start",
        "Gun Time",
        "time",
        "event_name",
        "race",
        "venue",
        "date",
        "url",
        "provider",
    ]]
    known_athlete_results.to_csv(path.join(OUT, "known_athlete_results.csv"))
    print(known_athlete_results)

if __name__ == "__main__":
    main()