from extractor.searches import *

if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = get_authenticated_service()
    keyword = input('Enter a keyword: ')
    search_videos_comments_by_keyword(service=service, max_pages=1, q=keyword, part='id, snippet', eventType='completed', type='video')