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

from datetime import datetime
import re
import os
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

class MineralPydiaCrawl:
    _num_page = 0
    _base_url = "https://www.dakotamatrix.com/mineralpedia"
    _main_window = ""
    _driver = None
    _urls = []
    _mineral_dict = dict()
    _outfile = "./MineralPydiaCrawlData.csv"

    def __init__(self, num_page, outfile=None):

        if outfile is not None:
            try:
                if outfile.strip()[-3:] is not "csv":
                    raise OSError
                with open(outfile, "w") as file:
                    file.close()

                self._outfile = outfile
            except OSError as ose:
                self._log(
                    "Path name provided for output file was not a valid path."
                    "Using the following default path and file name:\n"
                    "File name: MineralPydiaData.csv\n"
                    "Absolute path: " + os.path.abspath(self._outfile)
                )

        if num_page == '*':
            self._num_page = 293
        elif str(type(num_page)) == "<class 'int'>" or re.compile("^[0-9]+$").fullmatch(num_page) is not None:
            if int(num_page) < 1:
                self._log("Must crawl at least one page.", -1)
            elif int(num_page) > 293:
                self._log("Number of pages exceed actual pages, crawling max number of pages.")
                self._num_page = 293
            else:
                self._num_page = num_page
        else:
            self._log("Invalid value for number of pages, exiting crawl.", -1)

        self._log(
            "Initializing crawl with " + str(num_page)
            + " number of pages. Output file will be found at the following path: "
            + os.path.abspath(self._outfile)
        )

        profile = webdriver.FirefoxProfile()
        profile.set_preference("dom.disable_open_during_load", False)
        options = Options()
        options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        self._driver = webdriver.Firefox(firefox_profile=profile, options=options)

        self._crawl()
        self._driver.close()

        self._log("The crawl has completed without fatal error", 0)


    def _crawl(self):
        for i in range(1, self._num_page + 1):
            page_url = self._base_url + "?page=" + str(i)
            self._driver.get(page_url)
            self._log("Crawler proceeds to page #" + str(i))

            WebDriverWait(self._driver, 30).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.block-title h2 a"))
            )

            # cast generator to list to avoid potential stale elements
            urls = list(self._driver.find_elements(By.CSS_SELECTOR, "div.block-title h2 a"))

            self._urls += [u.get_attribute("href") for u in urls]

        for url in self._urls:
            self._fill_dict(url)

        self._fill_csv()


    def _fill_dict(self, url):
        mineral_info = dict()

        self._driver.get(url)


        WebDriverWait(self._driver, 30).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, "img.ism"))
        )

        name = url.split("/")[-1]
        self._log("Crawler is accessing entry page for the following mineral: " + name)

        try:
            habit = self._driver.find_element_by_xpath("//dt[text()='Crystal Habit']/following-sibling::dd").get_attribute("innerText")

            color = self._driver.find_element_by_xpath("//dt[text()='Color']/following-sibling::dd").get_attribute("innerText")

            streak = self._driver.find_element_by_xpath("//dt[text()='Streak']/following-sibling::dd").get_attribute("innerText")

            class_type = self._driver.find_element_by_xpath("//dt[text()='Class']/following-sibling::dd").get_attribute("innerText")

            hardness = self._driver.find_element_by_xpath("//dt[text()='Hardness']/following-sibling::dd/span").get_attribute("innerText")
        except NoSuchElementException as nsee:
            self._log("The crawler encountered a page missing required information for the following mineral: " + name)
            return

        try:
            fracture = self._driver.find_element_by_xpath("//dt[text()='Fracture']/following-sibling::dd").get_attribute("innerText")
        except NoSuchElementException as nsee:
            self._log(
                "The crawler encountered a page missing a fracture descriptor for the following mineral: " + name
                + "\nThe crawler will still include this entry, this log message is for debugging purposes."
            )
            fracture = None

        images = self._driver.find_elements_by_css_selector("a.catalog-thumb")

        img_urls = [image.get_attribute("href") for image in images]

        mineral_info["habit"] = habit.replace("\xa0", "")
        mineral_info["color"] = color.replace("\xa0", "")
        mineral_info["streak"] = streak.replace("\xa0", "")
        mineral_info["class"] = class_type.replace("\xa0", "")
        mineral_info["fracture"] = fracture.replace("\xa0", "")

        # trick to get around some issues with extracting string from generator
        mineral_info["hardness"] = hardness.replace("\xa0", "")
        mineral_info["hardness"] = np.mean([float(h) for h in mineral_info["hardness"].replace("\xa0", "").split("-")])
        mineral_info["images"] = img_urls

        self._mineral_dict[name] = mineral_info

        self._log(
            "Crawler has collected data for the following mineral\nName: " + name + "\nNumber of Image URIs: "
            + str(len(mineral_info["images"]))
        )


    def _fill_csv(self):
        names = []
        habits = []
        colors = []
        streaks = []
        classes = []
        fractures = []
        hardnesses = []
        images = []

        for mineral in self._mineral_dict:
            for url in self._mineral_dict[mineral]["images"]:
                names.append(mineral)
                habits.append(self._mineral_dict[mineral]["habit"])
                colors.append(self._mineral_dict[mineral]["color"])
                streaks.append(self._mineral_dict[mineral]["streak"])
                classes.append(self._mineral_dict[mineral]["class"])
                fractures.append(self._mineral_dict[mineral]["fracture"])
                hardnesses.append(self._mineral_dict[mineral]["hardness"])
                images.append(url)

        dump = {
            "name": names,
            "habit": habits,
            "color": colors,
            "streak": streaks,
            "class": classes,
            "fracture": fractures,
            "hardness": hardnesses,
            "image_uri": images
        }

        df = pd.DataFrame.from_dict(dump)
        df.to_csv(self._outfile, index=False)

        self._log(
            "Resultant data has been succesfully written to the following path: " + os.path.abspath(self._outfile)
        )



    def _log(self, log_string, exit_code=None):
        with open("./MetalPydiaCrawl.log", 'a') as file:
            if exit_code is not None:
                file.write(
                    "[" + datetime.now().isoformat() + "] > The program exited with exit code: " + str(exit_code)
                )
                file.close()
                exit(exit_code)

            if self._driver is None:
                file.write(
                    "[" + datetime.now().isoformat() + "] > "
                    + log_string.strip().replace("\n", "\n\t") + "\n"
                )
            else:
                file.write(
                    "[" + datetime.now().isoformat() + " @ "+ self._driver.current_url + "] > "
                    + log_string.strip().replace("\n", "\n\t") + "\n"
                )

            file.close()


def main():
    crawler = MineralPydiaCrawl(1)


if __name__ == "__main__":
    main()