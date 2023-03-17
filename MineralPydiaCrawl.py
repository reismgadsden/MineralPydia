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
    * All images URIs associated with each crystal
"""

import re
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException

class MineralPydiaCrawl:
    _num_page = 0
    _base_url = "https://www.dakotamatrix.com/mineralpedia"
    _main_window = ""
    _driver = ""
    _urls = []
    _mineral_dict = dict()

    def __init__(self, num_page):

        if num_page == '*':
            self._num_page = 293
        elif str(type(num_page)) == "<class 'int'>" or re.compile("^[0-9]+$").fullmatch(num_page) is not None:
            if int(num_page) < 1:
                print("Must crawl at least one page!")
                exit(0)
            elif int(num_page) > 293:
                print("Number of pages exceed actual pages, crawling max number of pages!")
                self._num_page = 293
            else:
                self._num_page = num_page
        else:
            print("Invalid value for number of pages!")
            exit(0)

        profile = webdriver.FirefoxProfile()
        profile.set_preference("dom.disable_open_during_load", False)
        options = Options()
        options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        self._driver = webdriver.Firefox(firefox_profile=profile, options=options)

        self._init_crawl()
        self._driver.close()


    def _init_crawl(self):
        for i in range(1, self._num_page + 1):
            page_url = self._base_url + "?page=" + str(i)
            self._driver.get(page_url)

            WebDriverWait(self._driver, 30).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.block-title h2 a"))
            )

            # cast generator to list to avoid potential stale elements
            urls = list(self._driver.find_elements(By.CSS_SELECTOR, "div.block-title h2 a"))

            self._urls += [u.get_attribute("href") for u in urls]

        for url in self._urls:
            self._fill_dict(url)


    def _fill_dict(self, url):
        mineral_info = dict()

        self._driver.get(url)

        WebDriverWait(self._driver, 30).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, "dt"))
        )

        name = url.split("/")[-1]

        try:
            habit = self._driver.find_element_by_xpath("//dt[text()='Crystal Habit']/following-sibling::dd").get_attribute("innerText")

            color = self._driver.find_element_by_xpath("//dt[text()='Color']/following-sibling::dd").get_attribute("innerText")

            streak = self._driver.find_element_by_xpath("//dt[text()='Streak']/following-sibling::dd").get_attribute("innerText")

            class_type = self._driver.find_element_by_xpath("//dt[text()='Class']/following-sibling::dd").get_attribute("innerText")

            hardness = self._driver.find_element_by_xpath("//dt[text()='Hardness']/following-sibling::dd/span").get_attribute("innerText")
        except NoSuchElementException as nsee:
            return

        try:
            fracture = self._driver.find_element_by_xpath("//dt[text()='Fracture']/following-sibling::dd").get_attribute("innerText")
        except NoSuchElementException as nsee:
            fracture = None

        images = self._driver.find_elements_by_css_selector("a.catalog-thumb")

        img_urls = [image.get_attribute("href") for image in images]

        mineral_info["habit"] = habit.replace("\xa0", "")
        mineral_info["color"] = color.replace("\xa0", "")
        mineral_info["streak"] = streak.replace("\xa0", "")
        mineral_info["class"] = class_type.replace("\xa0", "")
        mineral_info["fracture"] = fracture.replace("\xa0", "")
        mineral_info["hardness"] = hardness.replace("\xa0", "")
        mineral_info["hardness"] = np.mean([float(h) for h in mineral_info["hardness"].replace("\xa0", "").split("-")])
        mineral_info["images"] = img_urls

        self._mineral_dict[name] = mineral_info



def main():
    crawler = MineralPydiaCrawl(1)


if __name__ == "__main__":
    main()