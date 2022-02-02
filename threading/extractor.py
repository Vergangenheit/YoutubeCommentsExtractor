# TODO

# !/usr/bin/env python3
import concurrent.futures
import logging
from queue import Queue
from typing import List, Optional
import threading
from threading import Event
import time
from googleapiclient.discovery import Resource, build
import csv
import codecs
import config


def get_authenticated_service() -> Resource:
    service: Resource = build('youtube', 'v3', developerKey=config.API_KEY)

    return service


def get_videos(service: Resource, max_pages: int, k: str):
    final_results = []
    results = service.search().list(q=k, part='id, snippet', eventType='completed', type='video').execute()

    i = 0
    while results and i < max_pages:
        final_results.extend(results['items'])

        # check if another page exists
        if 'nextPageToken' in results:
            pageToken = results['nextPageToken']
            results = service.search().list(q=k, part='id, snippet', eventType='completed', type='video',
                                            pageToken=pageToken).execute()
            i += 1
        else:
            break

    return final_results


def get_video_comments_multiples(service: Resource, videoId: str, textFormat: str) -> Optional[List]:
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
        return comments
    except Exception as e:
        print(e)


def producer(service: Resource, k: str, queue: Queue, event: Event):
    """gets the videos"""
    while not event.is_set():
        results = get_videos(service, 1, k)
        for item in results:
            title = item['snippet']['title']
            video_id = item['id']['videoId']
            logging.info("Producer got video: %s %s", video_id, title)
            queue.put((video_id, title))

    logging.info("Producer received event. Exiting")


def consumer(service: Resource, queue_videos: Queue, queue_comments: Queue, event_vid: Event, event_com: Event):
    """ Pretend we're saving a number in the database. """
    while not event_vid.is_set() or not queue_videos.empty():
        video_id, title = queue_videos.get()
        logging.info(
            "Consumer storing message: %s (size=%d)", video_id + ' ' + title, queue_videos.qsize()
        )
        while event_com.is_set():
            comments = get_video_comments_multiples(service, videoId=video_id, textFormat='plainText')
            for comment in comments:
                queue_comments.put((video_id, title, comment))
                logging.info(
                    "Consumer storing comment: %s (size=%d)", comment, queue_comments.qsize()
                )

    # print(len(final_results))
    # print(final_results[:10])
    logging.info("Consumer received event. Exiting")


def writer(queue_comments: Queue, event: Event):
    while not event.is_set() or not queue_comments.empty():
        with codecs.open('../comments.csv', 'a', encoding='utf-8', errors='ignore') as comments_file:
            comments_writer = csv.writer(comments_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            video_id, title, comment = queue_comments.get()
            logging.info("Writing comment: %s", comment)
            comments_writer.writerow([video_id, title, comment])

    logging.info("Writer received event. Exiting")


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    t0: float = time.perf_counter()
    youtube: Resource = get_authenticated_service()
    queue_videos = Queue(maxsize=10)
    queue_comments = Queue(maxsize=30)
    event_vid = threading.Event()
    event_com = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(producer, youtube, 'David Goggins', queue_videos, event_vid)
        executor.submit(consumer, youtube, queue_videos, queue_comments, event_vid, event_com)
        executor.submit(writer, queue_comments, event_com)
        time.sleep(0.1)
        logging.info("Main: about to set video event")
        event_vid.set()
        time.sleep(0.1)
        logging.info("Main: about to set comments event")
        event_com.set()

    t1: float = time.perf_counter()
    print(f"Done in {t1 - t0}")
