import google.oauth2.credentials
import config
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import os


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(config.CLIENT_SECRETS_FILE, config.SCOPES)
    credentials = flow.run_console()

    return build(config.API_SERVICE_NAME, config.API_VERSION, credentials=credentials)


if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = get_authenticated_service()
