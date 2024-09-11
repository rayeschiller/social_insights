import argparse

from follower_insights import fetch_follower_demographics, write_demographics_to_csv
from reel_insights import fetch_media_data, aggregate_media_data, generate_filename
from secrets import ACCESS_TOKEN, USER_ID
from write_to_file import write_to_excel


def fetch_and_write_follower_insights(access_token):
    metrics = ["engaged_audience_demographics", "follower_demographics"]

    for metric in metrics:
        print("Grabbing audience insight data")
        demographics = fetch_follower_demographics(USER_ID, access_token, metric)
        print(f"Writing {metric} data to csv")
        write_demographics_to_csv(demographics, metric)


def fetch_and_write_reel_insights(access_token, paginate):
    print("Fetching media data")

    media_items = fetch_media_data(access_token, USER_ID, paginate)
    print(f"Fetched {len(media_items)} media items")
    print("Aggregating data")
    aggregated_data = aggregate_media_data(media_items, access_token)
    print(f"Aggregated {len(aggregated_data)} items")
    print("Writing to spreadsheet")
    file_path = generate_filename()
    write_to_excel(aggregated_data, file_path, include_images=True)
    print(f"Successfully wrote to spreadsheet at {file_path}")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fetch Instagram media insights")
    parser.add_argument("--access_token", type=str, required=False, help="Instagram Graph API access token")
    parser.add_argument("--paginate", action="store_true", help="Paginate through all media items")
    parser.add_argument("--no_images", action="store_true", help="Exclude images in the Excel file")

    args = parser.parse_args()
    paginate = args.paginate or False
    access_token = args.access_token if args.access_token else ACCESS_TOKEN
    include_images = not args.no_images  # Include images unless --no_images is passed

    fetch_and_write_reel_insights(access_token, paginate)
    fetch_and_write_follower_insights(access_token)

if __name__ == '__main__':
    main()
