from os import path

from bs4 import BeautifulSoup
from pandas import DataFrame
import requests

def fetch(url: str) -> str:
    cached_file_path = url
    for chr in ["<", ">", ":", "\"", "/", "\\", "|", "?"]:
        cached_file_path = cached_file_path.replace(chr, "_")
    cached_file_path = path.join("download-cache", cached_file_path)
    if path.isfile(cached_file_path):
        with open(cached_file_path, "r") as cached_file:
            return cached_file.read()
    result = requests.get(url)
    content = result.text
    with open(cached_file_path, "w") as cached_file:
        cached_file.write(content)
    return content

def parse(content: str) -> DataFrame:
    soup = BeautifulSoup(content, features = "lxml")
    table = soup.find(id = "individualResults")
    table_head = table.find("thead")
    columns = table_head.find_all("th")
    columns = [column.text.strip() for column in columns]
    data: dict[str, list[str]] = dict(zip(columns, [[] for _ in columns]))
    table_body = table.find("tbody")
    rows = table_body.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        cells = [cell.text.strip() for cell in cells]
        for column, cell in zip(columns, cells):
            data[column].append(cell)
    return DataFrame(data = data)

if __name__ == "__main__":
    url = "https://www.hubertiming.com/results/2022Flat"
    content = fetch(url)
    data = parse(content)
    print(data)