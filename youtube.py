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

# Replace with the scope you want to use
SCOPES = ["[https://www.googleapis.com/auth/youtube.force-ssl"]

app = Flask(__name__)
youtube = None  # Global variable for YouTube API client

# Add a route to serve the main page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results')
def results():
    # some code to generate results
    return render_template('results.html')

def authenticate_user():
    # Create a flow object
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", SCOPES)

    # Run the flow to get the credentials
    credentials = flow.run_local_server(port=0)  # Localhost setup for OAuth 2.0

    return credentials

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
            "client_id": os.getenv("CLIENT_ID", "YOUR_CLIENT_ID"),
            "project_id": os.getenv("PROJECT_ID", "YOUR_PROJECT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": os.getenv("CLIENT_SECRET", "YOUR_CLIENT_SECRET"),
            "redirect_uris": [
                "http://localhost:10000/",  # Default redirect URI
                "http://localhost:8080/redirect"  # Additional redirect URI
            ]
        }
    }

    with open("client_secrets.json", "w") as f:
        json.dump(client_secrets, f)

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

    # Create a YouTube API client
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    # Start the Flask server
    app.run(port=5000)

if __name__ == "__main__":
    main()