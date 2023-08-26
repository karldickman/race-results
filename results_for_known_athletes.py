#!/usr/bin/env python

from os import path

from pandas import read_csv

IN = "in"
OUT = "out"

if __name__ == "__main__":
    names = read_csv(path.join(IN, "canonical_names.csv"))
    races = read_csv(path.join(OUT, "huber_timing_races.csv"))
    results = read_csv(path.join(OUT, "huber_timing_results.csv"))
    known_athlete_results = names.set_index("name").join(results.set_index("Name"))
    known_athlete_results = known_athlete_results.loc[:, [
        "athlete",
        "Place",
        "Bib",
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
    known_athlete_results = known_athlete_results.set_index("URL").join(races.set_index("URL"))
    known_athlete_results.to_csv(path.join(OUT, "known_athlete_results.csv"))
    print(known_athlete_results)