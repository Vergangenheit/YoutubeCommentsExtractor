import config
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle


def get_authenticated_service() -> Resource:
    service: Resource = build('youtube', 'v3', developerKey=config.API_KEY)

    return service


if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service: Resource = get_authenticated_service()
