from os import path

import pdfkit
import requests

from directories import DOWNLOADS, FACSIMILES

def safe_file_name(url: str, extension: str) -> str:
    file_name = url
    for chr in ["<", ">", ":", "\"", "/", "\\", "|", "?"]:
        file_name = file_name.replace(chr, "_")
    return file_name + "." + extension

def fetch(url: str) -> str:
    cached_file_name = safe_file_name(url, "html")
    cached_file_path = path.join(DOWNLOADS, cached_file_name)
    if path.isfile(cached_file_path):
        with open(cached_file_path, "r") as cached_file:
            return cached_file.read()
    result = requests.get(url)
    content = result.text
    with open(cached_file_path, "w") as cached_file:
        cached_file.write(content)
    return content

def save_facsimile(url: str) -> None:
    file_name = safe_file_name(url, "pdf")
    facsimile_path = path.join(FACSIMILES, file_name)
    if not path.isfile(facsimile_path):
        pdfkit.from_url(url, facsimile_path, { "orientation": "Landscape" })

def download_race_results(url: str) -> str:
    save_facsimile(url)
    return fetch(url)
