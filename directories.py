from os import mkdir, path

DOWNLOADS = "download-cache"
FACSIMILES = "facsimiles"
IN = "in"
OUT = "out"

if __name__ == "__main__":
    for dir in [DOWNLOADS, FACSIMILES, OUT]:
        if not path.exists(dir):
            mkdir(dir)