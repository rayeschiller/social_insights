import csv

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

    with open('Documents/reel_insights.csv', mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['caption', 'title', 'value', 'description', 'type']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Process each media item
        for item in media_data.get('data', []):
            if item['media_type'] == 'VIDEO':
                media_id = item['id']
                resp = get_ig_media_insights(media_id)
                insights_data = resp.get('data', [])
                caption = item.get("caption").split('\n')[0]
                print(f"===== {caption} ======")
                for insight in insights_data:
                    row = {
                        'caption': caption,
                        'title': insight.get("title", ""),
                        'value': insight.get("values")[0].get("value", 0),
                        'description': insight.get("description", ""),
                        'type': insight.get("name", "")
                    }
                    writer.writerow(row)


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
