import asyncio
from asyncio import Queue, Task, AbstractEventLoop
from aiogoogle import Aiogoogle, GoogleAPI
from aiogoogle.models import Response, Request
import config
from typing import List, Dict, Coroutine, Any
import time
import csv
import codecs
import os


async def get_videos(k: str, part: str, eventType: str, type: str) -> str:
    async with Aiogoogle(api_key=config.API_KEY) as aiog:
        youtube: GoogleAPI = await aiog.discover('youtube', 'v3')
        req: Request = youtube.search.list(q=k, part=part, eventType=eventType, type=type)
        res: Dict = await aiog.as_api_key(req)
    items: List[Dict] = res.get('items')
    n: int = len(items)
    for item in items:
        videoId: str = item.get('id').get('videoId')
        return videoId


async def get_video_comments(videoId: str, textFormat: str, q: Queue) -> None:
    comments: List = []
    while True:
        async with Aiogoogle(api_key=config.API_KEY) as aiocomments:
            youtube: GoogleAPI = await aiocomments.discover('youtube', 'v3')
            req = youtube.commentThreads.list(videoId=videoId, part='snippet', textFormat=textFormat)
            results: Dict = await aiocomments.as_api_key(req)

        for item in results.get('items'):
            comment: str = item['snippet']['topLevelComment']['snippet']['textDisplay']
            t: float = time.perf_counter()
            await q.put((comment, t))


async def get_video_comments_multiples(k: str, part: str, eventType: str, type: str, textFormat: str) -> List:
    comments: List = []

    async with Aiogoogle(api_key=config.API_KEY) as aiocomments:
        youtube: GoogleAPI = await aiocomments.discover('youtube', 'v3')
        videoId = await get_videos(k, part, eventType, type)
        req = youtube.commentThreads.list(videoId=videoId, part='snippet', textFormat=textFormat)
        results: Coroutine[Dict] = await aiocomments.as_api_key(req)
        while results:
            for item in results.get('items'):
                comment: str = item['snippet']['topLevelComment']['snippet']['textDisplay']
                # put comment in list
                comments.append(comment)
            if 'nextPageToken' in results:
                pageToken = results['nextPageToken']
                req = youtube.commentThreads.list(videoId=videoId, part='snippet', textFormat=textFormat,
                                                  pageToken=pageToken)
                results: Dict = await aiocomments.as_api_key(req)
            else:
                break
    print(comments[:10])
    print(len(comments))


def write_to_csv(output_filename: str, comments: List[str]):
    """
        Write the extracted content into the file
    """
    try:
        with codecs.open(output_filename, 'w', encoding='utf-8', errors='ignore') as comments_file:
            comments_writer = csv.writer(comments_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in comments:
            comments_writer.writerow(list(row))
    except FileNotFoundError:
        print("Output file not present", output_filename)
        print("Current dir: ", os.getcwd())
        raise FileNotFoundError


async def main(keyword: str, part: str, eventType: str, type: str, textFormat: str):
    await get_video_comments_multiples(keyword, part, eventType, type, textFormat)


if __name__ == "__main__":
    # asyncio.run(get_videos(q='David Goggins', part='id, snippet', eventType='completed',
    #                                   type='video'))
    t0: float = time.perf_counter()
    loop: AbstractEventLoop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(keyword='David Goggins', part='id, snippet', eventType='completed', type='video', textFormat='plainText'))
    # asyncio.run(
    #     main(keyword='David Goggins', part='id, snippet', eventType='completed', type='video', textFormat='plainText'))
    t1: float = time.perf_counter()
    print(f"Done in {t1 - t0}")
    # Done in 138.7081521
