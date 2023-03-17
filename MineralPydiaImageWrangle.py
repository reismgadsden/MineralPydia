"""
MineralPydiaImageWrangle.py

This program will download all images from the image URIs collected in MineralPydiaCrawl.py.
"""

# http requests
import urllib.request
from urllib.error import URLError

# access csv
import pandas as pd

# logging
from datetime import datetime
import os

# used for loading
import threading
import time

"""
ENVIRONMENT VARIABLES.

CSV_PATH - the csv to load in.
IMG_DUMP_PATH - the directory to download images to.
"""
CSV_PATH = "./MineralPydiaCrawlData.csv"
IMG_DUMP_PATH = "./img_dump"


# downloads the images
def metal_pydia_image_wrangler(csv_path, img_dump_path):
    """
    metal_pydia_image_wrangler

    Uses the image URIs gathered to download mineral images.

    :param csv_path: the path of the csv to read from.
    :param img_dump_path: the directory path which all images will be downloaded to.
    """

    # initializes df variable, not necessary but wanted to avoid PEP8 warnings in PyCharm
    df = ""

    # attempt to read the csv and store in df variable
    try:
        df = pd.read_csv(csv_path)

    # if the file does not exist log the path and EXIT
    except FileNotFoundError:
        log("Could not find the csv located at the following path: " + os.path.abspath(csv_path), -4)

    # if the filename is not a valid file name, log the path and EXIT
    except OSError:
        log("The file path, " + os.path.abspath(csv_path) + " is not a valid path.", -5)

    # if the image dump path does not exist, log that it does not exist and use default directory instead
    if not os.path.exists(img_dump_path):
        log(
            "Could not find the image dump directory located at the following path: "
            + os.path.abspath(img_dump_path) + ". Using the default directory instead."
        )
        img_dump_path = "./img_dump"

    # create a subset of the data only containing the image uri and name and loop over it
    index = 1
    for uri, filename in df[["image_uri", "image_name"]].itertuples(index=False):

        # attempt to download the image, log the attempt and log if it is successfully
        try:
            log("Attempting to fetch the following:\n" + "URL: " + uri + "\n" + "Filename: " + filename)

            # start download in new thread to allow command line spinning wheel
            t1 = threading.Thread(target=urllib.request.urlretrieve, args=(uri, img_dump_path + "/" + filename))
            t1.start()

            # creates a spinning wheel in the command prompt, makes waiting less depressing
            val = 0
            out = "Downloading image " + str(index) + " out of " + str(len(df)) + ": "
            while t1.is_alive():
                val = val % 4
                os.system('cls')

                if val == 0:
                    print(out + "|")
                elif val == 1:
                    print(out + "/")
                elif val == 2:
                    print(out + "-")
                else:
                    print(out + "\\")

                val += 1
                time.sleep(0.1)

            log(
                "Image " + filename + " downloaded successfully to the following path: "
                + os.path.abspath(img_dump_path + "/" + filename)
            )
            index += 1

        # if an error is caught, log it and EXIT
        except URLError as ue:
            log("Encountered unexpected URLError: " + str(ue), -1)

    # log that all images have been downloaded and EXIT
    log("All image URIs have been processed. Resultant images are stored in: " + os.path.abspath(img_dump_path), 0)


# logging
def log(log_string, exit_code=None):
    """
    log

    function used to dump strings into the log file

    :param log_string: the string to be dumped to log file
    :param exit_code: allows us to log an exit code and exit with that code, logs both errors and successes
    """

    # append to log
    with open("MetalPydiaImageWrangle.log", "a") as file:

        # log a string with no exit code
        file.write(
            "[" + datetime.now().isoformat() + "]>" + log_string.strip().replace("\n", "\n\t") + "\n"
        )

        # if an exit code is provided we can log that exit code and exit using that code
        if exit_code is not None:
            file.write(
                "[" + datetime.now().isoformat() + "]> The program exited with exit code: " + str(exit_code) + "\n"
            )

            file.close()
            exit(exit_code)

        file.close()


def main():
    """
    main

    Initializes the downloads.
    """
    metal_pydia_image_wrangler(CSV_PATH, IMG_DUMP_PATH)


if __name__ == "__main__":
    """
    Executes main if not being imported.
    """
    main()
