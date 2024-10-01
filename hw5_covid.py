
#Import libraries

import requests
import json
import time
from datetime import datetime, timedelta
import statistics 


states_list = ['al','ar','as','az','ca','co','ct', 'dc','de','fl','ga','gu','hi','ia','id','il','in','ks','ky','la','ma','md','me', 'mi', 'mn', 'mo','mp','ms', 'mt', 'nc', 'nd', 'ne', 'nh', 'nj', 'nm','nv','ny','oh','ok','or', 'pa', 'pr','ri', 'sc','sd','tn', 'tx', 'ut', 'va','vi','vt','wa','wi','wv', 'wy']


results = []


#1. URLS for api
url1 = 'https://api.covidtracking.com/v1/states/'
url2 = '/daily.json'

#2. Variables to call needed data
confirmed_covid_cases = "positive"
positive_cases = "positiveIncrease"


#3. Iterate over each state in the list and fetch the data
for state_key in states_list:
    url = url1 + state_key + url2  # Put the URL together

    # Fetch the JSON data from the API
    req = requests.get(url)
    state_data = json.loads(req.text)

    if state_data:

        #Q1a. Extract positive case increases for each day
        positive_increases = [day[positive_cases] for day in state_data if day[positive_cases] is not None]

        #Q1b. Average number of new daily confirmed cases
        avg_daily_cases = statistics.mean(positive_increases) 

        #Q2. Date with the highest new number of covid cases
        highest_cases_date = max(state_data, key=lambda x: x[positive_cases])
        date_highest_cases = datetime.strptime(str(highest_cases_date['date']), "%Y%m%d").strftime("%Y-%m-%d")

        #Q3. Most recent date with no new covid cases
        no_new_cases_date = next((day for day in state_data if day[positive_cases] == 0), None)
        if no_new_cases_date:
            date_no_new_cases = datetime.strptime(str(no_new_cases_date['date']), "%Y%m%d").strftime("%Y-%m-%d")
        else:
            date_no_new_cases = "No days with 0 new cases"

        #Q4. Monthly cases calculation
        monthly_cases = {}
        for day in state_data:
            date_str = str(day['date'])
            month_str = date_str[:6]  # Get YYYYMM
            if month_str not in monthly_cases:
                monthly_cases[month_str] = 0
            monthly_cases[month_str] += day[positive_cases] if day[positive_cases] else 0

        #Q5. Month with the highest new number of covid cases
        month_highest_cases = max(monthly_cases, key=monthly_cases.get)
        month_lowest_cases = min(monthly_cases, key=monthly_cases.get)

        #Convert month from YYYYMM to a more readable format
        month_highest_readable = datetime.strptime(month_highest_cases, "%Y%m").strftime("%B %Y")
        month_lowest_readable = datetime.strptime(month_lowest_cases, "%Y%m").strftime("%B %Y")

        #Output the results to see if everything is working correctly
        print(f"Covid confirmed cases statistics for {state_key.upper()}:\n")
        print(f"Average number of new daily confirmed cases: {avg_daily_cases:.2f}")
        print(f"Date with the highest new number of covid cases: {date_highest_cases} with {highest_cases_date[positive_cases]} cases")
        print(f"Most recent date with no new covid cases: {date_no_new_cases}")
        print(f"Month with the highest new number of covid cases: {month_highest_readable} with {monthly_cases[month_highest_cases]} cases")
        print(f"Month with the lowest new number of covid cases: {month_lowest_readable} with {monthly_cases[month_lowest_cases]} cases")
        print("\n" + "="*50 + "\n")

        state_results = {
            "state": state_key.upper(),
            "avg_daily_cases": avg_daily_cases,
            "date_highest_cases": date_highest_cases,
            "highest_cases_count": highest_cases_date[positive_cases],
            "date_no_new_cases": date_no_new_cases,
            "month_highest_cases": month_highest_readable,
            "highest_cases_month_count": monthly_cases[month_highest_cases],
            "month_lowest_cases": month_lowest_readable,
            "lowest_cases_month_count": monthly_cases[month_lowest_cases],
        }
        results.append(state_results)
    else:
        print(f"No data available for {state_key.upper()}")

#6. Export the results to a JSON file
with open('covid_statistics.json', 'w') as f:
    json.dump(results, f, indent=4)