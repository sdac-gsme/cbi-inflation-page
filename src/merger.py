"""
merger.py: This script reads and merges the annual and monthly inflation data, 
cleans and processes it, and generates the merged tables. The processed data 
is then saved as CSV files in the 'merged_data' directory.
"""
from pathlib import Path
import pandas as pd

DATA_DIR = Path().joinpath("data")

JALALI_MONTHS = {
    'فروردين': 1,
    'ارديبهشت': 2,
    'خرداد': 3,
    'تير': 4,
    'مرداد': 5,
    'شهريور': 6,
    'مهر': 7,
    'آبان': 8,
    'آذر': 9,
    'دی': 10,
    'بهمن': 11,
    'اسفند': 12,
}

def create_annual_table() -> pd.DataFrame:
    """
    Read and process the annual inflation table.

    Returns:
    - table: Processed annual inflation table as a DataFrame.
    """
    table = pd.read_csv(DATA_DIR.joinpath("raw_data", "annual.csv"))
    table.columns = ["Year", "CPI", "Annual_Inflation"]
    table["Year"] = table["Year"].astype(int)
    table = table.set_index("Year")
    table = table.sort_index()
    return table

def create_monthly_table() -> pd.DataFrame:
    """
    Read and process the monthly inflation tables.

    Returns:
    - merged_table: Merged and processed monthly inflation table as a DataFrame.
    """
    monthly_tables = DATA_DIR.joinpath("raw_data", "monthly_tables")
    df_list = []
    years = []
    for path in monthly_tables.iterdir():
        dataframe = pd.read_csv(path)
        dataframe = clean_monthly_dataframe(dataframe)
        df_list.append(dataframe)
        years.append(int(path.name.replace(".csv", "")))
    merged_table = pd.concat(df_list, keys=years, names=["Year", "Month"])
    merged_table = merged_table.sort_index()

    return merged_table

def clean_monthly_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and process the monthly inflation dataframe.

    Args:
    - dataframe: Monthly inflation dataframe to be cleaned.

    Returns:
    - dataframe: Cleaned monthly inflation dataframe.
    """
    dataframe.columns = ["Month", "CPI", "Annual_Inflation"]
    dataframe["Month"] = dataframe["Month"].map(JALALI_MONTHS)
    dataframe = dataframe.set_index("Month")
    return dataframe

if __name__ == "__main__":
    merged_data_dir = DATA_DIR.joinpath("merged_data")
    merged_data_dir.mkdir(exist_ok=True)
    annual_table = create_annual_table()
    annual_table.to_csv(merged_data_dir.joinpath("annual_table.csv"))
    monthly_table = create_monthly_table()
    monthly_table.to_csv(merged_data_dir.joinpath("monthly_table.csv"))
