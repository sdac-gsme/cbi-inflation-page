"""
This file contains the scraper script that fetches and saves inflation data 
from the website of the central bank.
"""
from pathlib import Path
import time

from bs4 import BeautifulSoup

import pandas as pd

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from webdriver_manager.firefox import GeckoDriverManager


ROOT_DIR = Path()
RAW_DATA_DIR = ROOT_DIR.joinpath("data", "raw_data")


def folders_initialization():
    """Create necessary folders"""
    monthly_tables = RAW_DATA_DIR.joinpath("monthly_tables")
    monthly_tables.mkdir(parents=True, exist_ok=True)


def transform_html_to_table(table_soup: BeautifulSoup) -> pd.DataFrame:
    """Transform HTML table to pandas DataFrame"""
    rows = table_soup.find_all("tr")
    cells = list(map(lambda x: x.find_all("td"), rows))
    table = pd.DataFrame(cells).applymap(lambda cell: cell.text)
    return table


def clean_table(table: pd.DataFrame) -> pd.DataFrame:
    """Clean and process the table data"""
    table = table.apply(lambda s: s.str.replace("\n", "").str.strip())
    table = table.set_axis(labels=table.iloc[0], axis="columns").iloc[1:]
    table = table.set_index(table.columns[0])
    table = table.replace("-.-", None)
    table = table.astype(float)
    return table


class InflationPage:
    """
    This class provides methods to fetch and save inflation data from the 
    website of the central bank.
    """
    def __init__(self, driver: webdriver.Firefox) -> None:
        self.driver = driver
        url = "https://www.cbi.ir/Inflation/Inflation_FA.aspx"
        driver.get(url)
        self.soup = self._get_page_soup()

    def update_data(self):
        """Update the inflation data by fetching and saving the necessary tables"""
        self._save_selectable_years()
        self._save_annual_inflation_table()
        years = self._get_missing_years_list()
        for year in years:
            self._select_and_save_monthly_table(year)

    def _get_page_soup(self) -> BeautifulSoup:
        """Retrieve the parsed HTML soup of the current page"""
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        while soup.find("select") is None:
            time.sleep(0.1)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
        time.sleep(0.5)
        return soup

    def _save_selectable_years(self) -> None:
        """Save the selectable years as a CSV file"""
        year_series = self._get_selecteable_years()
        year_series.to_csv(RAW_DATA_DIR.joinpath("years.csv"))

    def _get_selecteable_years(self) -> pd.Series:
        """Retrieve the selectable years from the page"""
        year_list = self.soup.find("select").find_all("option")
        year_dict = {int(year["value"]): year.text for year in year_list}
        year_series = pd.Series(year_dict, name="Year")
        year_series.index.name = "Value"
        return year_series

    def _save_annual_inflation_table(self) -> None:
        """Save the annual inflation table as a CSV file"""
        print("Getting Annual Inflation Table")
        table = self._extract_annual_inflation_table()
        table.to_csv(RAW_DATA_DIR.joinpath("annual.csv"))

    def _extract_annual_inflation_table(self) -> pd.DataFrame:
        """Extract the annual inflation table from the page"""
        table_soup = self.soup.find_all("table")[-1]
        table = transform_html_to_table(table_soup)
        table = clean_table(table)
        return table

    def _save_monthly_inflation_table(self, year) -> None:
        """Save the monthly inflation table for a specific year as a CSV file"""
        print(f"Getting Monthly Inflation Table for {year}")
        no_found_id = "ctl00_ucBody_ucContent_ctl00_LblNotFound"
        if self.soup.find("span", {"id": no_found_id}) is not None:
            return
        table = self._extract_monthly_inflation_table()
        table.to_csv(RAW_DATA_DIR.joinpath("monthly_tables", f"{year}.csv"))

    def _extract_monthly_inflation_table(self) -> pd.DataFrame:
        """Extract the monthly inflation table from the page"""
        table_soup = self.soup.find("table")
        table = transform_html_to_table(table_soup)
        table = clean_table(table)
        return table

    def _select_year_by_value(self, year):
        """Select a specific year from the dropdown menu"""
        select_element = self.driver.find_element(By.TAG_NAME, "select")
        Select(select_element).select_by_value(str(int(year)))
        self.soup = self._get_page_soup()

    def _select_and_save_monthly_table(self, year):
        """Select and save the monthly table for a specific year"""
        self._select_year_by_value(year)
        self._save_monthly_inflation_table(year)

    def _get_missing_years_list(self) -> list:
        """Get the list of missing years that need to be fetched"""
        all_years = self._get_selecteable_years().index.to_list()
        monthly_folder = RAW_DATA_DIR.joinpath("monthly_tables")
        available_files = [path.name for path in monthly_folder.iterdir()]
        available_years = [int(file_name.replace(".csv", "")) for file_name in available_files]
        missing_years = [year for year in all_years[:-1] if year not in available_years]
        missing_years.append(all_years[-1])
        return missing_years


if __name__ == "__main__":
    folders_initialization()
    service=FirefoxService(GeckoDriverManager().install())
    options = Options()
    options.add_argument('-headless')
    with webdriver.Firefox(service=service, options=options) as web_driver:
        scraper = InflationPage(web_driver)
        scraper.update_data()
