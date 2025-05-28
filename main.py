# Import necessary libraries
import argparse
import requests
from fuzzywuzzy import fuzz
from tabulate import tabulate
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

# Define API endpoint and resource ID
API_URL = "https://data.gov.au/data/api/3/action/datastore_search"
RESOURCE_ID = "55ad4b1c-5eeb-44ea-8b29-d410da431be3"

def fetch_data(limit=100):
    """
    Fetches business records from the data.gov.au API using pagination.

    Args:
        limit (int): The maximum number of records to fetch.

    Returns:
        list: A list of business records.
    """
    records = []
    offset = 0
    print(f"Fetching {limit} reords for this task")
    while True:
        params = {
            'resource_id': RESOURCE_ID,
            'limit': limit,
            'offset': offset
        }
        print(f"Fetching records....")
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get('success', False):
            raise Exception("API call unsuccessful.")

        result = data['result']
        batch = result.get('records', [])
        records.extend(batch)

        if len(records) == limit: 
            break  # No more records to fetch
        offset += limit
    print(f"Fetching complete")        
    return records

def filter_data(records, state=None, status=None, registered_after=None):
    """
    Filters records based on state, business status, and registration date.

    Args:
        records (list): The list of business records.
        state (str): Filter for a specific state.
        status (str): Filter for a specific business status.
        registered_after (datetime): Filter records registered after this date.

    Returns:
        list: A filtered list of business records.
    """
    def record_filter(record):
        if state and record.get('BN_STATE_OF_REG') != state:
            return False
        if status and record.get('BN_STATUS') != status:
            return False
        if registered_after:
            date_str = record.get('BN_REG_DT')
            if date_str:
                try:
                    record_date = datetime.strptime(date_str, '%d/%m/%Y')
                    if record_date < registered_after:
                        return False
                except:
                    return False
        return True

    return [r for r in records if record_filter(r)]

def similar_names(records, query, limit=10):
    """
    Performs similarity matching on business names.

    Args:
        records (list): The list of business records.
        query (str): The business name to search for.
        limit (int): Maximum number of similar results to return.

    Returns:
        list: A list of matching business records sorted by similarity.
    """
    if not query:
        return records[:limit]
    scored = [(r, fuzz.token_sort_ratio(query.lower(), r.get('BN_NAME', '').lower())) for r in records]
    scored.sort(key=lambda x: (-int(query.lower() == x[0].get('BN_NAME', '').lower()), -x[1]))
    return [s[0] for s in scored[:limit]]

def list_view(records):
    """
    Displays records in a tabular list format.

    Args:
        records (list): The list of business records to display.
    """
    table = [[r.get('BN_NAME'), r.get('BN_STATE_OF_REG'), r.get('BN_STATUS'), r.get('BN_REG_DT')] for r in records]
    print(tabulate(table, headers=["Name", "State", "Status", "Registered"], tablefmt="grid"))

def histogram_view(records):
    """
    Displays a histogram of business counts per state.

    Args:
        records (list): The list of business records to analyze.
    """
    states = [r.get('BN_STATE_OF_REG') for r in records if r.get('BN_STATE_OF_REG')]
    counts = Counter(states)
    plt.bar(counts.keys(), counts.values())
    plt.title("Businesses per State")
    plt.xlabel("State")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def chart_view(records):
    """
    Displays a line chart of business registrations over time.

    Args:
        records (list): The list of business records to analyze.
    """
    years = []
    for r in records:
        date_str = r.get('BN_REG_DT')
        if date_str:
            try:
                year = datetime.strptime(date_str, '%d/%m/%Y').year
                years.append(year)
            except:
                continue
    year_counts = Counter(years)
    sorted_years = sorted(year_counts)
    counts = [year_counts[y] for y in sorted_years]
    plt.plot(sorted_years, counts, marker='o')
    plt.title("Business Registrations Over Time")
    plt.xlabel("Year")
    plt.ylabel("Number of Registrations")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    """
    Main function to parse arguments and coordinate the data retrieval, filtering,
    matching, and display based on user input.
    """
    parser = argparse.ArgumentParser(description="Explore Australian Business Names Register")
    parser.add_argument("--state", help="Filter by state (e.g. VIC, NSW)")
    parser.add_argument("--status", help="Filter by status (e.g. Registered, Cancelled)")
    parser.add_argument("--after", help="Filter by registration date after (YYYY-MM-DD)")
    parser.add_argument("--name", help="Search for similar business names")
    parser.add_argument("--view", choices=["list", "histogram", "chart"], default="list", help="Display mode")
    parser.add_argument("--limit", type=int, default=10, help="Limit number of results")

    args = parser.parse_args()

    try:
        after_date = datetime.strptime(args.after, '%Y-%m-%d') if args.after else None
    except ValueError:
        print("[ERROR] Date must be in format YYYY-MM-DD")
        return

    records = fetch_data(limit=max(args.limit, 100))

    if not records:
        print("[INFO] No data retrieved.")
        return

    records = filter_data(records, state=args.state, status=args.status, registered_after=after_date)
    records = similar_names(records, args.name, limit=args.limit)

    if args.view == "list":
        list_view(records)
    elif args.view == "histogram":
        histogram_view(records)
    elif args.view == "chart":
        chart_view(records)

if __name__ == "__main__":
    main()
