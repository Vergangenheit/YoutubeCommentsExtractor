from extractor.service import get_authenticated_service
from extractor.store_comments import write_to_csv
import os
from googleapiclient.discovery import Resource
import time

def get_videos(service, max_pages, **kwargs):
    final_results = []
    results = service.search().list(**kwargs).execute()

    i = 0
    while results and i < max_pages:
        final_results.extend(results['items'])

        # check if another page exists
        if 'nextPageToken' in results:
            kwargs['pageToken'] = results['nextPageToken']
            results = service.search().list(**kwargs).execute()
            i += 1
        else:
            break

    return final_results


def get_video_comments(service, **kwargs):
    comments = []
    try:
        results = service.commentThreads().list(**kwargs).execute()

        while results:
            for item in results['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

            if 'nextPageToken' in results:
                kwargs['pageToken'] = results['nextPageToken']
                results = service.commentThreads().list(**kwargs).execute()
            else:
                break

    except Exception as e:
        print(e)

    return comments


def get_video_comments_multiples(service: Resource, videoId: str, textFormat: str):
    comments = []
    try:
        results = service.commentThreads().list(videoId=videoId, part='snippet', textFormat=textFormat).execute()

        while results:
            for item in results['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

            if 'nextPageToken' in results:
                pageToken = results['nextPageToken']
                results = service.commentThreads().list(videoId=videoId, part='snippet', textFormat=textFormat,
                                                  pageToken=pageToken).execute()
            else:
                break

    except Exception as e:
        print(e)

    print(comments)


def search_videos_by_keyword(service, **kwargs):
    results = get_videos(service, **kwargs)
    for item in results:
        print('%s - %s' % (item['snippet']['title'], item['id']['videoId']))


def search_videos_comments_by_keyword(service, max_pages, **kwargs):
    results = get_videos(service, max_pages, **kwargs)
    final_results = []
    for item in results:
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        print('%s - %s' % (title, video_id))
        comments = get_video_comments(service, part='snippet', videoId=video_id, textFormat='plainText')
        final_results.extend([(video_id, title, comment) for comment in comments])
        # print(comments)

    write_to_csv(final_results)


if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    # keyword = input('Enter a keyword: ')
    t0: float = time.perf_counter()
    service = get_authenticated_service()
    get_video_comments_multiples(service, videoId='5tSTk1083VY', textFormat='plainText')
    t1: float = time.perf_counter()
    print(f"Done in {t1 - t0}")
    # search_videos_comments_by_keyword(service=service, max_pages=1, q=keyword, part='id, snippet',
    #                                   eventType='completed',
    #                                   type='video')
