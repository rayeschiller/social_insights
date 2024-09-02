import csv
import datetime
import os
import requests
from settings import ACCESS_TOKEN, USER_ID


def get_ig_media(access_token, user_id):
    """ Fetch media insights for an Instagram Business or Creator account. """
    media_url = f"https://graph.facebook.com/v20.0/{user_id}/media"
    media_params = {
        'fields': 'caption,comments_count,is_shared_to_feed,owner,username,media_type',
        'access_token': access_token
    }

    media_response = requests.get(media_url, params=media_params)
    media_data = media_response.json()

    aggregated_data = {}

    # Process each media item
    for item in media_data.get('data', []):
        if item['media_type'] == 'VIDEO':
            media_id = item['id']
            resp = get_ig_media_insights(media_id)
            insights_data = resp.get('data', [])
            caption = item.get("caption")
            # caption = item.get("caption").split('\n')[0]

            # Initialize the dictionary for this caption if not already done
            if caption not in aggregated_data:
                aggregated_data[media_id] = {
                    "Accounts reached": None,
                    "Comments": None,
                    "Likes": None,
                    "Saved": None,
                    "Shares": None,
                    "Initial Plays": None,
                    "Reels interactions": None,
                    "Video View Total Time (milliseconds)": None,
                    "Reels Average Watch Time (milliseconds)": None,
                    "Total Plays": None,
                    "Replays": None,
                    "Like PCT": None,
                    "Comment PCT": None,
                    "Share PCT": None,
                    "Save PCT": None
                }

            for insight in insights_data:
                title = insight.get("title", "")
                value = insight.get("values")[0].get("value", 0)
                if title in aggregated_data[media_id]:
                    aggregated_data[media_id][title] = value

            # Calculate PCT values
            total_plays = aggregated_data[media_id]["Total Plays"] or 1  # Avoid division by zero
            aggregated_data[media_id]["Like PCT"] = (aggregated_data[media_id]["Likes"] or 0) / total_plays * 100
            aggregated_data[media_id]["Comment PCT"] = (aggregated_data[media_id][
                                                           "Comments"] or 0) / total_plays * 100
            aggregated_data[media_id]["Share PCT"] = (aggregated_data[media_id][
                                                         "Shares"] or 0) / total_plays * 100
            aggregated_data[media_id]["Save PCT"] = (aggregated_data[media_id]["Saved"] or 0) / total_plays * 100

    # Define the headers based on the desired output
    headers = [
        "media_id", "caption", "Accounts reached", "Comments", "Likes", "Saved", "Shares",
        "Initial Plays", "Reels interactions", "Video View Total Time (milliseconds)",
        "Reels Average Watch Time (milliseconds)", "Total Plays", "Replays"
    ]

    # Write the aggregated data to the CSV
    file_path = os.path.expanduser(f'~/Documents/personalDev/reel_insights/{datetime.date}.csv')
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for caption, metrics in aggregated_data.items():
            row = {"media_id": media_id}
            row.update(metrics)
            writer.writerow(row)
    print(f"Finished writing to {file_path}")


def get_ig_media_insights(media_id):
    media_insights_url = f"https://graph.facebook.com/v20.0/{media_id}/insights"
    media_params = {
        'metric': 'reach,comments,likes,saved,shares,plays,total_interactions,ig_reels_video_view_total_time,'
                  'ig_reels_avg_watch_time,ig_reels_aggregated_all_plays_count,clips_replays_count,'
                  'ig_reels_aggregated_all_plays_count,',
        'access_token': ACCESS_TOKEN
    }

    resp = requests.get(media_insights_url, params=media_params)
    resp.raise_for_status()
    return resp.json()


if __name__ == '__main__':
    get_ig_media(ACCESS_TOKEN, USER_ID)
