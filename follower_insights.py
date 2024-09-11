import csv
import datetime
import os

import requests

from secrets import USER_ID


def fetch_follower_demographics(ig_user_id, access_token, metric):
    """Fetch follower demographics for an Instagram user."""
    insights_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/insights"

    params = {
        'metric': metric,
        'period': 'lifetime',
        'timeframe': 'this_month',
        'breakdown': 'city',
        'metric_type': 'total_value',
        'access_token': access_token
    }

    try:
        response = requests.get(insights_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()['data']

        # Extract the relevant information from the response
        if data and len(data) > 0:
            demographics = data[0]['total_value']['breakdowns'][0]['results']
            return demographics
        else:
            return []

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def write_demographics_to_csv(demographics, metric):
    """Write demographics data to a CSV file."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    file_name = "follower_cities" if metric == "follower_demographics" else "engaged_audience_cities"
    file_path = os.path.expanduser(
        f'~/Documents/personalDev/reel_insights/additional_insights/{file_name}_{today}.csv')

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['city', 'region', 'value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for city_data in demographics:
            city_region = city_data['dimension_values'][0].split(', ')
            city = city_region[0]
            region = city_region[1] if len(city_region) > 1 else ''
            writer.writerow({
                'city': city,
                'region': region,
                'value': city_data['value']
            })

    print(f"Data written to {file_path}")
