#!/usr/bin/env python

from os import path

from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance
from pandas import DataFrame, read_csv

from directories import IN, OUT

if __name__ == "__main__":
    athletes: list[str] = list(read_csv(path.join(IN, "athletes.csv"))["Athlete"])
    names: list[str] = list(read_csv(path.join(OUT, "huber_timing_people.csv"))["Name"])
    matches = {
        "athlete": [],
        "name": [],
        "distance": [],
    }
    for athlete in athletes:
        for name in names:
            distance = normalized_damerau_levenshtein_distance(athlete.upper(), name)
            if distance < 0.3:
                matches["athlete"].append(athlete)
                matches["name"].append(name)
                matches["distance"].append(distance)
    distances = DataFrame(data = matches)
    distances = distances.sort_values(by = ["distance"])
    distances.to_csv(path.join(OUT, "huber_athlete_associations.csv"))
    print(distances)