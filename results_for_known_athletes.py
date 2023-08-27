#!/usr/bin/env python

from os import path

from pandas import isnull, read_csv

from directories import IN, OUT

if __name__ == "__main__":
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
    results = read_csv(path.join(OUT, "huber_timing_results.csv"))
    known_athlete_results = athletes \
        .set_index("name") \
        .join(results.set_index("Name")) \
        .reset_index() \
        .loc[:, [
            "athlete",
            "from",
            "to",
            "notes",
            "Gender",
            "Age",
            "Time to Start",
            "Gun Time",
            "Time",
            "URL",
        ]]
    known_athlete_results.to_csv(path.join(OUT, "known_athlete_results.csv"))
    # Associate results with race metadata
    races = read_csv(path.join(OUT, "huber_timing_races.csv"), parse_dates = ["Date"], dtype = {
        "Race": "string",
        "Location": "string",
        "Host": "string",
        "URL": "string",
    })
    known_athlete_results = known_athlete_results \
        .set_index("URL") \
        .join(races.set_index("URL")) \
        .reset_index()
    # Tag whether they were members of the team
    known_athlete_results["team_member"] = (known_athlete_results["from"] <= known_athlete_results["Date"]) \
        & ((known_athlete_results["to"] >= known_athlete_results["Date"]) \
           | (isnull(known_athlete_results["to"])))
    known_athlete_results = known_athlete_results.loc[:, [
        "athlete",
        "notes",
        "team_member",
        "Gender",
        "Age",
        "Time to Start",
        "Gun Time",
        "Time",
        "Race",
        "Location",
        "Date",
        "URL",
    ]]
    known_athlete_results.to_csv(path.join(OUT, "known_athlete_results.csv"))
    print(known_athlete_results)