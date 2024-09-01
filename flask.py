from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, to authorize Instagram, go to /login'


@app.route('/login')
def login():
    auth_url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=user_profile,user_media"
        f"&response_type=code"
    )

    scope="instagram_basic,instagram_content_publish,instagram_manage_comments,instagram_manage_insights,pages_show_list,pages_read_engagement"
    fb_auth_url = f'https://www.facebook.com/dialog/oauth?client_id={APP_ID}&display=page&redirect_uri={REDIRECT_URI}&response_type=token&scope={scope}'
    print(f"Redirecting to: {auth_url}")
    return webbrowser.open(fb_auth_url)

@app.route('/oauth')
def oauth():
    code = request.args.get('code')
    if not code:
        return 'No code provided', 400

    url = 'https://api.instagram.com/oauth/access_token'
    payload = {
        'client_id': APP_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code': code
    }
    response = requests.post(url, data=payload)
    data = response.json()
    if 'access_token' in data:
        # Here you can store the access token and user_id as needed
        return f'Access Token: {data["access_token"]}<br>User ID: {data["user_id"]}'
    else:
        return 'Failed to obtain access token', 500


@app.route("/insights")
def insights():
    get_ig_media(ACCESS_TOKEN, USER_ID)

