# CBI Inflation Page
The cbi-inflation-page package is designed to fetch and merge inflation data from the website of the central bank. It consists of two main scripts: scraper.py and merger.py.

## Requirements
Before using the package, please ensure that Firefox is installed on your system.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/sdac-gsme/cbi-inflation-page.git
```
2. Change into the project directory:
```
cd cbi-inflation-page
```
3. Install the required dependencies by running the following command:
```bash
pip install -r requirements.txt
```

## Usage
1. Fetching Data
To retrieve data from the central bank's website, run the following command:

```bash
python src/scraper.py
```

This command will initiate the scraper script, which will fetch the inflation data and store it in a local file.

2. Merging and Cleaning Data
After fetching the data, you can merge and clean it using the following command:

```bash
python src/merger.py
```

The merger script will read the data fetched by the scraper, perform the necessary merging operations, and generate cleaned data.

Note: Make sure to run the scraper.py script before executing the merger.py script to ensure that the latest data is available for merging.
