import urllib.request
from urllib.error import URLError, HTTPError, ContentTooShortError
import pandas as pd
from datetime import datetime
import os


def metal_pydia_image_wrangler(csv_path="./MineralPydiaCrawlData.csv", img_dump_path="./img_dump"):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError as fnfe:
        log("Could not find the csv located at the following path: " + os.path.abspath(csv_path), -4)

    if not os.path.exists(img_dump_path):
        log(
            "Could not find the image dump directory located at the following path: "
            + os.path.abspath(img_dump_path) + ". Using the default directory instead."
        )
        img_dump_path = "./img_dump"

    for uri, filename in df[["image_uri", "image_name"]].itertuples(index=False):
        try:
            log("Attempting to fetch the following:\n" + "URL: " + uri + "\n" + "Filename: " + filename)
            urllib.request.urlretrieve(uri, img_dump_path + "/" + filename)
            log(
                "Image " + filename + " downloaded succesfully to the following path: "
                + os.path.abspath(img_dump_path + "/" + filename)
            )
        except URLError as ue:
            log("Encountered unexpected URLError: " + str(ue), -1)
        except HTTPError as he:
            log("Encountered unexpected HTTPError: " + str(he), -2)
        except ContentTooShortError as ctse:
            log("Encountered unexcepted ContentTooShortError: " + str(ctse), -3)

    log("All image URIs have been processed. Resultant images are stored in: " + os.path.abspath(img_dump_path), 0)


def log(log_string, exit_code=None):
    with open("MetalPydiaImageWrangle.log", "a") as file:

        file.write(
            "[" + datetime.now().isoformat() + "]>" + log_string.strip().replace("\n", "\n\t") + "\n"
        )

        if exit_code is not None:
            file.write(
                "[" + datetime.now().isoformat() + "]> The program exited with exit code: " + str(exit_code) + "\n"
            )

            file.close()
            exit(exit_code)

        file.close()

if __name__ == "__main__":
    metal_pydia_image_wrangler()
