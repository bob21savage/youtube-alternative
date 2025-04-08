# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from flask import Flask, request, jsonify
from flask import render_template, redirect, url_for
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with full YouTube access scope
SCOPES = ["https://www.googleapis.com/auth/youtube"]

app = Flask(__name__)
youtube = None  # Global variable for YouTube API client

# Add a route to serve the main page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/results', methods=['GET'])
def results():
    query = request.args.get('query', '').strip()
    if not query:
        return render_template('results.html', results=[])
    
    # Perform search using the YouTube API
    response = youtube.search().list(
        part="id,snippet",
        q=query,
        type="video"
    ).execute()
    
    return render_template('results.html', results=response.get('items', []))

def authenticate_user():
    try:
        # Create a flow object
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json", SCOPES)

        # Dynamically set the redirect URI
        redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:3000/")
        print(f"Using redirect URI: {redirect_uri}")  # Log the redirect URI
        flow.redirect_uri = redirect_uri

        # Run the flow to get the credentials with access_type=offline
        credentials = flow.run_local_server(port=3000, access_type="offline")  # Request offline access

        return credentials
    except FileNotFoundError:
        print("Error: 'client_secrets.json' file not found. Please ensure it exists and is correctly configured.")
        exit(1)
    except google_auth_oauthlib.flow.FlowExchangeError as e:
        if "access_denied" in str(e):
            print("Error: Access was denied by the user.")
        else:
            print(f"Error during authentication: {e}")
        exit(1)

@app.route('/search', methods=['POST'])
def search_endpoint():
    global youtube
    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Create a request to search for videos
    response = youtube.search().list(
        part="id,snippet",
        q=query,
        type="video"
    ).execute()

    # Return the results as JSON
    return jsonify(response)

def search_videos(youtube, query):
    # Create a request to search for videos
    request = youtube.search().list(
        part="id,snippet",
        q=query,
        type="video"
    )

    # Execute the request
    response = request.execute()

    # Print the results
    for item in response["items"]:
        print(f"Title: {item['snippet']['title']}")
        print(f"Video ID: {item['id']['videoId']}")

def create_client_secrets():
    client_secrets = {
        "installed": {
            "client_id": os.getenv("CLIENT_ID"),
            "project_id": os.getenv("PROJECT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": os.getenv("CLIENT_SECRET"),
            "redirect_uris": [
                os.getenv("REDIRECT_URI")  # Use only the environment variable
            ]
        }
    }

    # Validate client secrets before writing to file
    if not all([client_secrets["installed"]["client_id"], 
                client_secrets["installed"]["client_secret"], 
                client_secrets["installed"]["redirect_uris"][0]]):
        print("Error: CLIENT_ID, CLIENT_SECRET, or REDIRECT_URI is missing. Please check your .env file.")
        exit(1)

    with open("client_secrets.json", "w") as f:
        json.dump(client_secrets, f)

def check_granted_scopes(credentials):
    # List of scopes your application requested
    requested_scopes = set(SCOPES)

    # Scopes granted by the user
    granted_scopes = set(credentials.scopes)

    # Determine which scopes were granted
    granted_scopes_dict = {
        "YouTube Readonly": "https://www.googleapis.com/auth/youtube.readonly" in granted_scopes
    }

    print("Granted Scopes:")
    for scope, granted in granted_scopes_dict.items():
        print(f"{scope}: {'Granted' if granted else 'Not Granted'}")

    # Log any missing scopes
    missing_scopes = requested_scopes - granted_scopes
    if missing_scopes:
        print("The following requested scopes were not granted:")
        for scope in missing_scopes:
            print(f"- {scope}")

def main():
    global youtube
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    try:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    except googleapiclient.errors.HttpError as e:
        print(f"Error: {e}")

    # Create client_secrets.json dynamically
    create_client_secrets()

    # Authenticate the user
    credentials = authenticate_user()

    # Check granted scopes
    check_granted_scopes(credentials)

    # Create a YouTube API client
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    # Start the Flask server
    app.run(port=3000)

if __name__ == "__main__":
    main()