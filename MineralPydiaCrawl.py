"""
MineralPydiaCrawl.py

This program will crawl the informational site on Dakota Matrix Minerals "Mineralpedia".
It will collect all available information for each mineral including:
    * Crystal Habit
    * Color
    * Streak
    * Class
    * Fracture (Can be none)
    * Hardness
    * All images URIs associated with each mineral

author: Reis Mercer Gadsden
"""

# logging usage
from datetime import datetime

# user input validation
import re
import os

# data manipulation and storage
import pandas as pd
import numpy as np

# selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

import psutil


"""
ENVIRONMENT VARIABLES

OUTPUT - The output file to write to, must be a csv. If left None use default path (./MineralPydiaCrawlData.csv).
NUM_PAGES - The number of pages to gather from. If the value is "*" then the maximum amount of pages are crawled to.
            All other values must be an integer.
"""
OUTPUT = None
NUM_PAGES = "*"
RAM_USAGE_CAP = 60.0


# class MineralPydiaCrawl
class MineralPydiaCrawl:
    """
    MineralPydiaCrawl

    Master class that makes all calls to needed functions.
    """

    # number of pages to crawl
    _num_page = 0

    # base url for the wiki
    _base_url = "https://www.dakotamatrix.com/mineralpedia"

    # variable that will hold the webdriver object once user input is validated
    _driver = None

    # holds all the mineral urls
    _urls = []

    # holds all the mineral data
    _mineral_dict = dict()

    # csv that the output will be written to
    _outfile = "./MineralPydiaCrawlData.csv"

    def __init__(self, num_page, outfile):
        """
        __init__

        Initialization of MineralPydiaCrawl object.

        :param num_page: the number of pages to crawl to.
        :param outfile: output path of the resultant data.
        """

        # sanitize outfile input if it is not left empty
        if not (outfile is None):

            # verifies that the outfile is csv format
            # also verifies that the path is a valid one
            try:
                if not(outfile.strip()[-3:] == "csv"):
                    raise OSError

                with open(outfile, "w") as file:
                    file.close()

                self._outfile = outfile

            # log that the input was invalid, use default path and DO NOT exit
            except OSError:
                self._log(
                    "Path name provided for output file was not a valid path."
                    "Using the following default path and file name:\n"
                    "File name: MineralPydiaData.csv\n"
                    "Absolute path: " + os.path.abspath(self._outfile)
                )

        # attempt to sanitize num pages input
        # if the input is "*" set to the max number of pages (293 as of 2023/03/17)
        if num_page == '*':
            self._num_page = 293

        # if the input passed is an integer or the string of integer, make sure it is within acceptable parameters
        elif str(type(num_page)) == "<class 'int'>" or re.compile("^[0-9]+$").fullmatch(num_page) is not None:

            # if the value is less then one, log the runtime error and EXIT
            if int(num_page) < 1:
                self._log("Must crawl at least one page.", -1)

            # if the value is greater than the max, log it and DO NOT exit. Use max number of pages instead
            elif int(num_page) > 293:
                self._log("Number of pages exceed actual pages, crawling max number of pages.")
                self._num_page = 293

            # if the value is within possible values, set class variable as input
            else:
                self._num_page = num_page

        # catch any invalid input, log it, and EXIT
        else:
            self._log("Invalid value for number of pages, exiting crawl.", -1)

        print("Initializing Crawl...")

        # log the number of pages to be crawled and the output file path
        self._log(
            "Initializing crawl with " + str(num_page)
            + " number of pages. Output file will be found at the following path: "
            + os.path.abspath(self._outfile)
        )

        # set up the Firefox profile
        profile = webdriver.FirefoxProfile()
        profile.set_preference("dom.disable_open_during_load", False)

        # define the executable location for Firefox (this maybe commented out if it is throwing errors)
        options = Options()
        options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

        # hide Selenium window
        options.add_argument("--headless")

        # create the webdriver object with given profile and options
        self._driver = webdriver.Firefox(firefox_profile=profile, options=options)

        # initialize the crawl
        self._crawl()

        # terminate Selenium window
        self._driver.close()

        # log that the crawl has completed and EXIT
        self._log("The crawl has completed without fatal error", 0)

    # starts the crawl
    def _crawl(self):
        """
        _crawl

        Crawls the 'page' pages of Mineralpedia, collects all mineral urls, makes calls to extract and output data.
        """

        # iterate over the number of pages, this can be down with range due to the format of the page url(s)
        for i in range(1, self._num_page + 1):

            # progress bar to make us feel better
            os.system("cls")
            size = round(50 * (i / self._num_page))
            print(
                "Accessing page " + str(i) + " out of " + str(self._num_page)
                + "\n\nProgress:\t| " + '█' * size + ' ' * (50 - size) + " |"
            )

            # get the ith page
            page_url = self._base_url + "?page=" + str(i)

            # proceed to ith page, and log it
            self._driver.get(page_url)
            self._log("Crawler proceeds to page #" + str(i))

            # wait until all anchor tags associated with minerals have loaded
            WebDriverWait(self._driver, 30).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.block-title h2 a"))
            )

            # cast generator to list to avoid potential stale elements
            urls = list(self._driver.find_elements(By.CSS_SELECTOR, "div.block-title h2 a"))

            # append the urls to class list
            self._urls += [u.get_attribute("href") for u in urls]

        # gets the mineral info for each url collected
        index = 1
        for url in self._urls:

            # if ram usage exceeds cap:
            # * kill all firefox processes
            # * kill all geckodriver processes
            # * reinitialize the driver
            # this will free memory being used by Selenium allowing, trading off a little time
            ram_used = psutil.virtual_memory()[2]
            if ram_used >= RAM_USAGE_CAP:
                os.system("tskill firefox")
                os.system("tskill geckodriver")

                # set up the Firefox profile
                profile = webdriver.FirefoxProfile()
                profile.set_preference("dom.disable_open_during_load", False)

                # define the executable location for Firefox (this maybe commented out if it is throwing errors)
                options = Options()
                options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

                # hide Selenium window
                options.add_argument("--headless")

                # create the webdriver object with given profile and options
                self._driver = webdriver.Firefox(firefox_profile=profile, options=options)

            self._fill_dict(url)

            # progress bar to make us feel better
            os.system('cls')
            size = round(50 * (index / len(self._urls)))
            print(
                "Accessing mineral " + str(index) + " out of " + str(len(self._urls))
                + "\n\nProgress:\t| " + '█' * size + ' ' * (50 - size) + " |"
            )

            index += 1

        # fills the csv with all mineral data
        self._fill_csv()

    # fills class dictionary
    def _fill_dict(self, url):
        """
        _fill_dict

        Gets the mineral data from each inputted url.

        :param url: mineral url to collect data from
        """

        # create a dictionary to hold all data for one mineral
        mineral_info = dict()

        # proceed to the url
        self._driver.get(url)

        # wait until all images have loaded
        WebDriverWait(self._driver, 30).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, "img.ism"))
        )

        # get the name of mineral, and log it
        name = url.split("/")[-1]
        self._log("Crawler is accessing entry page for the following mineral: " + name)

        # this data is essential, so if one of these elements is not present we want to skip over it
        try:

            # gets the habit of the mineral
            # https://en.wikipedia.org/wiki/Crystal_habit
            habit = self._driver.find_element_by_xpath("//dt[contains(text(), 'Crystal Habit')]/following-sibling::dd")\
                .get_attribute("innerText")

            # gets the color descriptor of the mineral
            color = self._driver.find_element_by_xpath("//dt[contains(text(), 'Color')]/following-sibling::dd")\
                .get_attribute("innerText")

            # gets the streak descriptor of the mineral
            # the streak is the color of a crushed minerals powder
            streak = self._driver.find_element_by_xpath("//dt[contains(text(), 'Streak')]/following-sibling::dd")\
                .get_attribute("innerText")

            # gets the class of mineral that it belongs to
            # https://en.wikipedia.org/wiki/Crystal_system
            class_type = self._driver\
                .find_element_by_xpath("//dt[contains(text(), 'Crystal System')]/following-sibling::dd")\
                .get_attribute("innerText")

            # gets the hardness of mineral
            # https://en.wikipedia.org/wiki/Hardness
            hardness = self._driver\
                .find_element_by_xpath("//dt[contains(text(), 'Hardness')]/following-sibling::dd/span")\
                .get_attribute("innerText")

            pattern = re.compile("^[0-9]+(\\.[0-9]+)*(-[0-9]+(\\.[0-9]+)*)*$")
            if re.fullmatch(pattern, hardness.replace("\xa0", "")) is None:
                raise NoSuchElementException

        # if one to elements are not present return to go to the next url, log that the mineral had insufficient data
        except NoSuchElementException:
            self._log("The crawler encountered a page missing required information for the following mineral: " + name)
            return

        # this value was decided to be non-essential, but still wanted it to be included
        try:

            # gets the fracture descriptor of the mineral
            # https://en.wikipedia.org/wiki/Fracture_(mineralogy)
            fracture = self._driver.find_element_by_xpath("//dt[text()='Fracture']/following-sibling::dd")\
                .get_attribute("innerText")

        # if this element is not present, log it, and set it to None
        except NoSuchElementException:
            self._log(
                "The crawler encountered a page missing a fracture descriptor for the following mineral: " + name
                + "\nThe crawler will still include this entry, this log message is for debugging purposes."
            )
            fracture = None

        # gets all the images present on a mineral page
        images = self._driver.find_elements_by_css_selector("a.catalog-thumb")

        # list comprehension to create a list of image uris
        img_urls = [image.get_attribute("href") for image in images]

        # insert all data into necessary
        # need to strip \xa0, which is equivalent to &nbsp;
        mineral_info["habit"] = habit.replace("\xa0", "")
        mineral_info["color"] = color.replace("\xa0", "")
        mineral_info["streak"] = streak.replace("\xa0", "")
        mineral_info["class"] = class_type.replace("\xa0", "")

        if fracture is None:
            mineral_info["fracture"] = None
        else:
            mineral_info["fracture"] = fracture.replace("\xa0", "")

        mineral_info["images"] = img_urls

        # trick to get around some issues with extracting string from generator
        # hardness sometimes is given as a range of value i.e. 2-2.5
        # we will use the median value of range
        mineral_info["hardness"] = hardness.replace("\xa0", "")
        mineral_info["hardness"] = np.mean([float(h) for h in mineral_info["hardness"].replace("\xa0", "").split("-")])

        # add the dictionary to the classes master dictionary keyed on the mineral's name
        self._mineral_dict[name] = mineral_info

        # log that the page has been scraped, include the name and total number of image uris gathered
        self._log(
            "Crawler has collected data for the following mineral\nName: " + name + "\nNumber of Image URIs: "
            + str(len(mineral_info["images"]))
        )

    # output data to csv
    def _fill_csv(self):
        """
        _fill_csv

        Fills the output target with the data collected,
        """

        # holds the names of minerals
        names = []

        # holds the habits of minerals
        habits = []

        # holds the colors of minerals
        colors = []

        # holds the streaks of minerals
        streaks = []

        # holds the classes/systems of minerals
        classes = []

        # holds the fracture of minerals
        fractures = []

        # holds the hardness of minerals
        hardnesses = []

        # holds the image uris
        images = []

        # holds the actual filename of the image uris
        filenames = []

        # looping over each mineral in the dictionary
        for mineral in self._mineral_dict:

            # we want to loop over each image uri and duplicate its information
            for url in self._mineral_dict[mineral]["images"]:
                names.append(mineral)
                habits.append(self._mineral_dict[mineral]["habit"])
                colors.append(self._mineral_dict[mineral]["color"])
                streaks.append(self._mineral_dict[mineral]["streak"])
                classes.append(self._mineral_dict[mineral]["class"])
                fractures.append(self._mineral_dict[mineral]["fracture"])
                hardnesses.append(self._mineral_dict[mineral]["hardness"])
                images.append(url)
                filenames.append(url.split("/")[-1])

        # sets up a dictionary object to dumped to csv
        dump = {
            "name": names,
            "habit": habits,
            "color": colors,
            "streak": streaks,
            "class": classes,
            "fracture": fractures,
            "hardness": hardnesses,
            "image_uri": images,
            "image_name": filenames
        }

        # casts the dictionary to a Panda's DataFrame
        df = pd.DataFrame.from_dict(dump)

        # outputs Panda's DataFrame to a csv
        df.to_csv(self._outfile, index=False)

        # log that the data has been successfully dumped to a csv
        self._log(
            "Resultant data has been successfully written to the following path: " + os.path.abspath(self._outfile)
        )

    # logging function
    def _log(self, log_string, exit_code=None):
        """
        _log

        function used to dump strings into the log file

        :param log_string: the string to be dumped to log file
        :param exit_code: allows us to log an exit code and exit with that code, logs both errors and successes
        """

        # append to the log
        with open("./MetalPydiaCrawl.log", 'a') as file:

            # if the driver has not been initialized yet, we do not want to include a url
            if self._driver is None:
                file.write(
                    "[" + datetime.now().isoformat() + "]> "
                    + log_string.strip().replace("\n", "\n\t") + "\n"
                )
            # if the driver has been initialized we can get the current url for more accurate logging
            elif exit_code is None:
                file.write(
                    "[" + datetime.now().isoformat() + " @ " + self._driver.current_url + "]> "
                    + log_string.strip().replace("\n", "\n\t") + "\n"
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

    Initializes the crawl with given environment variables.
    """
    MineralPydiaCrawl(NUM_PAGES, OUTPUT)


if __name__ == "__main__":
    """
    Executes the main method if it is not being imported
    """
    main()
