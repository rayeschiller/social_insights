import csv
import os
import requests
import re
import datetime
from settings import ACCESS_TOKEN, USER_ID

METRICS = [
    "Caption",
    "Accounts reached",
    "Comments",
    "Likes",
    "Saved",
    "Shares",
    "Initial Plays",
    "Reels interactions",
    "Video View Total Time (milliseconds)",
    "Reels Average Watch Time (milliseconds)",
    "Total Plays",
    "Replays",
    "Like PCT",
    "Comment PCT",
    "Share PCT",
    "Save PCT",
    "Hashtags"
]

def fetch_media_data(access_token, user_id):
    """Fetch all media data for an Instagram Business or Creator account, handling pagination."""
    media_url = f"https://graph.facebook.com/v20.0/{user_id}/media"
    media_params = {
        'fields': 'caption,comments_count,is_shared_to_feed,owner,username,media_type',
        'access_token': access_token,
        'limit': 25  # Set a limit for each page; 25 is the default
    }

    all_media_items = []
    while media_url:
        response = requests.get(media_url, params=media_params)
        response.raise_for_status()
        data = response.json()
        all_media_items.extend(data.get('data', []))  # Add current page's items to the list

        # Get the next page URL from the response, if available
        media_url = data.get('paging', {}).get('next')

    return all_media_items


def fetch_media_insights(media_id):
    """Fetch insights for a specific media item."""
    media_insights_url = f"https://graph.facebook.com/v20.0/{media_id}/insights"
    media_params = {
        'metric': 'reach,comments,likes,saved,shares,plays,total_interactions,ig_reels_video_view_total_time,'
                  'ig_reels_avg_watch_time,ig_reels_aggregated_all_plays_count,clips_replays_count',
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(media_insights_url, params=media_params)
    response.raise_for_status()
    return response.json()['data']


def aggregate_media_data(media_items):
    """Aggregate media data and insights into a structured format."""
    aggregated_data = {}
    for item in media_items:
        if item['media_type'] == 'VIDEO':
            media_id = str(item['id'])
            caption = item.get("caption", "").split('\n')[0]
            hashtags = extract_hashtags(item.get("caption", ""))
            insights_data = fetch_media_insights(media_id)
            aggregated_data[media_id] = create_media_entry(caption, hashtags, insights_data)
            calculate_pct_values(aggregated_data[media_id])
    return aggregated_data


def extract_hashtags(caption):
    """Extract hashtags from a caption."""
    return ' '.join(re.findall(r'#\w+', caption))  # Find all hashtags and join them into a single string


def create_media_entry(caption, hashtags, insights_data):
    """Create an entry for a media item with its caption and insights."""
    entry = {metric: None for metric in METRICS}
    entry["Caption"] = caption
    entry["Hashtags"] = hashtags
    for insight in insights_data:
        title = insight.get("title", "")
        value = insight.get("values")[0].get("value", 0)
        if title in entry:
            entry[title] = value
    return entry


def calculate_pct_values(entry):
    """Calculate and format the PCT values for likes, comments, shares, and saves."""
    total_plays = entry["Total Plays"] or 1  # Avoid division by zero
    pct_metrics = {
        "Like PCT": "Likes",
        "Comment PCT": "Comments",
        "Share PCT": "Shares",
        "Save PCT": "Saved"
    }

    for pct_key, metric_key in pct_metrics.items():
        entry[pct_key] = f"{(entry[metric_key] or 0) / total_plays * 100:.2f}%"


def generate_filename():
    """Generate a filename with today's date."""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    return os.path.expanduser(f'~/Documents/personalDev/reel_insights/insights_{today}.csv')


def write_to_csv(aggregated_data, file_path):
    """Write the aggregated data to a CSV file."""
    headers = ["media_id"] + METRICS
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()  # Ensure header is written only once
        for media_id, metrics in aggregated_data.items():
            row = {"media_id": media_id}
            row.update(metrics)
            writer.writerow(row)


def main():
    media_items = fetch_media_data(ACCESS_TOKEN, USER_ID)
    aggregated_data = aggregate_media_data(media_items)
    file_path = generate_filename()
    write_to_csv(aggregated_data, file_path)


if __name__ == '__main__':
    main()
