#!/usr/bin/env python

from argparse import ArgumentParser
from os import path

from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance
from pandas import DataFrame, read_csv

from directories import IN, OUT

def main(athletes_file_path: str, names_file_path: str, output_file_path: str, maximum_distance: float):
    athletes: list[str] = list(read_csv(athletes_file_path)["Athlete"])
    names: list[str] = list(read_csv(names_file_path)["name"])
    matches = {
        "athlete": [],
        "name": [],
        "distance": [],
    }
    for athlete in athletes:
        comparable_athlete = athlete.lower()
        for name in names:
            comparable_name = name.lower()
            distance = normalized_damerau_levenshtein_distance(comparable_athlete, comparable_name)
            if distance < maximum_distance:
                matches["athlete"].append(athlete)
                matches["name"].append(name)
                matches["distance"].append(distance)
    distances = DataFrame(data = matches)
    distances = distances.sort_values(by = ["distance"])
    distances.to_csv(output_file_path)
    print(distances)

if __name__ == "__main__":
    parser = ArgumentParser(description = "Identifies close matches to a list of known athlete names using Damerau-Levenshtein distance.")
    parser.add_argument("--known-athletes", type = str, default = path.join(IN, "athletes.csv"), help = "The file containing a list of known athletes.")
    parser.add_argument("--names", type = str, default = path.join(OUT, "people.csv"), help = "The file containing the names to be matched with the known athletes.")
    parser.add_argument("--maximum-distance", type = float, default = 0.3, help = "The maximum normalized Damerau-Levenshtein distance to allow.")
    parser.add_argument("-o", "--out", type = str, help = "The output file")
    arguments = parser.parse_args()
    if not "people" in arguments.names:
        parser.error("Output file name could not be inferred, specify with --out.")
    out = arguments.out if arguments.out is not None else arguments.names.replace("people", "athlete_associations")
    main(arguments.known_athletes, arguments.names, out, arguments.maximum_distance)