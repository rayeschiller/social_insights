import datetime
import os
import re

import requests

from settings import METRICS


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
        entry[pct_key] = (entry[metric_key] or 0) / total_plays


def fetch_media_data(access_token, user_id, paginate=True):
    """Fetch media data for an Instagram Business or Creator account.
    """
    media_url = f"https://graph.facebook.com/v20.0/{user_id}/media"
    media_params = {
        'fields': 'caption,owner,media_type,timestamp,media_url,thumbnail_url,video_duration',
        'access_token': access_token,
        'limit': 25  # Set a limit for each page; 25 is the default
    }

    all_media_items = []
    while media_url:
        response = requests.get(media_url, params=media_params)
        response.raise_for_status()
        data = response.json()
        all_media_items.extend(data.get('data', []))  # Add current page's items to the list

        # If paginate is False, break after the first page
        if not paginate:
            break

        # Get the next page URL from the response, if available
        media_url = data.get('paging', {}).get('next')

    return all_media_items


def fetch_media_insights(media_id, access_token):
    """Fetch insights for a specific media item."""
    media_insights_url = f"https://graph.facebook.com/v20.0/{media_id}/insights"
    media_params = {
        'metric': 'reach,comments,likes,saved,shares,plays,total_interactions,ig_reels_video_view_total_time,'
                  'ig_reels_avg_watch_time,ig_reels_aggregated_all_plays_count,clips_replays_count',
        'access_token': access_token
    }
    response = requests.get(media_insights_url, params=media_params)
    response.raise_for_status()
    return response.json()['data']


def aggregate_media_data(media_items, access_token):
    """Aggregate media data and insights into a structured format."""
    aggregated_data = {}
    for item in media_items:
        if item['media_type'] == 'VIDEO':
            media_id = str(item['id'])
            caption = item.get("caption", "").split('\n')[0]
            hashtags = extract_hashtags(item.get("caption", ""))
            timestamp = format_timestamp(item.get("timestamp"))
            media_url = item.get("media_url")
            thumbnail_url = item.get("thumbnail_url")
            insights_data = fetch_media_insights(media_id, access_token)
            aggregated_data[media_id] = create_media_entry(
                caption, hashtags, timestamp, media_url, thumbnail_url, insights_data
            )
            calculate_pct_values(aggregated_data[media_id])
    return aggregated_data


def format_timestamp(timestamp):
    """Convert timestamp to a more readable format."""
    if timestamp:
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
        return dt.strftime("%Y-%m-%d")
    return None


def extract_hashtags(caption):
    """Extract hashtags from a caption."""
    return ' '.join(re.findall(r'#\w+', caption))  # Find all hashtags and join them into a single string


def create_media_entry(caption, hashtags, timestamp, media_url, thumbnail_url, insights_data):
    """Create an entry for a media item with its caption and insights."""
    entry = {metric: None for metric in METRICS}
    entry["Caption"] = caption
    entry["Timestamp"] = timestamp
    entry["Media URL"] = media_url
    entry["Thumbnail URL"] = thumbnail_url
    entry["Hashtags"] = hashtags
    for insight in insights_data:
        title = insight.get("title", "")
        value = insight.get("values")[0].get("value", 0)
        if title in entry:
            entry[title] = value
    return entry


def generate_filename(csv=False):
    """Generate a filename with today's date."""
    today = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    ext = "csv" if csv else "xlsx"
    return os.path.expanduser(f'~/Documents/personalDev/reel_insights/insights_{today}.{ext}')
