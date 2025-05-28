# Business Name Lookup Tool - Business Name Register CLI Utility

This is a command-line utility to explore and search the **Business Name Register** available at [data.gov.au][a link](https://data.gov.au/data/api/3/action/datastore_search?resource_id=55ad4b1c-5eeb-44ea-8b29-d410da431be3).

The tool provides:
- Filtering capabilities (state, status, registration date)
- Visual outputs (list, histogram, line chart)
- Fuzzy matching for business name search

---
### 1. Install Dependencies
pip install -r requirements.txt

### 2. Usage

python3 main.py [OPTIONS]

### 3. Available Options

Option	    Description<br />
--state	    Filter by state or territory (e.g., VIC, NSW)<br />
--status	Filter by business status (e.g., Registered, Unregistered)<br />
--after	    Filter by registration date (format: YYYY-MM-DD)<br />
--view	    Output mode: list, histogram, or chart. Default is list<br />
--name	    Fuzzy match a business name (in double quotes, example "ABC PTY LTD")<br />
--limit	    Limit number of records to retrieve, Default is 100.<br />

### 4. Examples

#### - List all registered businesses in VIC since 2001
python main.py --state VIC --status Registered --after 2001-01-01 --view list --limit 10000

#### - Show a registration trend over time
python main.py --view chart --limit 500

#### - Show a histogram of business counts by state
python main.py --view histogram --limit 1000

#### - Fuzzy match a business name
python main.py --name " 1-3684" --limit 5 --view list