import asyncio
from asyncio import Queue, Task, AbstractEventLoop
from aiogoogle import Aiogoogle, GoogleAPI
from aiogoogle.models import Response, Request
import config
from typing import List, Dict, Coroutine, Any, Tuple
import time
import csv
import codecs
import os
from multiprocessing import cpu_count
import concurrent.futures  # Allows creating new processes
from concurrent.futures import ProcessPoolExecutor, Future
import logging
import random
import colorama
import aiofiles


async def get_videos(k: str, part: str, eventType: str, type: str, data: Queue):
    async with Aiogoogle(api_key=config.API_KEY) as aiog:
        youtube: GoogleAPI = await aiog.discover('youtube', 'v3')
        req: Request = youtube.search.list(q=k, part=part, eventType=eventType, type=type)
        res: Dict = await aiog.as_api_key(req)
    items: List[Dict] = res.get('items')
    n: int = len(items)
    for item in items:
        videoId: str = item.get('id').get('videoId')
        title: str = item.get('snippet').get('title')
        logging.info(colorama.Fore.YELLOW + "Got videos %s - %s", videoId, title)
        await data.put((videoId, title))
        await asyncio.sleep(random.random() + .1)


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


async def get_video_comments_multiples(num: int, textFormat: str, data: Queue, comments: Queue):
    processed = 0
    while processed < num:
        videoId, title = await data.get()
        await asyncio.sleep(random.random() + .1)
        async with Aiogoogle(api_key=config.API_KEY) as aiocomments:
            youtube: GoogleAPI = await aiocomments.discover('youtube', 'v3')
            req = youtube.commentThreads.list(videoId=videoId, part='snippet', textFormat=textFormat)
            results: Coroutine[Dict] = await aiocomments.as_api_key(req)
            while results:
                for item in results.get('items'):
                    comment: str = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    logging.info(colorama.Fore.CYAN + "fetched comment %s", comment)
                    # put comment in list
                    await comments.put((videoId, title, comment))
                    logging.info(colorama.Fore.LIGHTBLUE_EX + "stored comment %s", comment)
                    await asyncio.sleep(random.random() + .5)
                    if 'nextPageToken' in results:
                        pageToken = results['nextPageToken']
                        logging.info(colorama.Fore.BLUE + "going into next page %s", pageToken)
                        req = youtube.commentThreads.list(videoId=videoId, part='snippet', textFormat=textFormat,
                                                          pageToken=pageToken)
                        results: Dict = await aiocomments.as_api_key(req)
                    else:
                        break


async def write_to_file(output_filename: str, comments: Queue):
    """
        Write the extracted content into the file
    """

    videoId, title, comment = await comments.get()
    logging.info(colorama.Fore.LIGHTGREEN_EX + "Got comment %s", comment)
    async with aiofiles.open(output_filename, 'a', encoding='utf-8', errors='ignore') as comments_file:
        # comments_writer.writerow(['Video ID', 'Title', 'Comment'])
        await comments_file.write(videoId + ', ' + title + ', ' + comment)
        logging.info(colorama.Fore.WHITE + "Wrote comment %s", comment)
            # except FileNotFoundError:
            #     print("Output file not present", output_filename)
            #     print("Current dir: ", os.getcwd())
            #     raise FileNotFoundError


def run(keyword: str, part: str, eventType: str, type: str, textFormat: str) -> List:
    comments = asyncio.run(get_video_comments_multiples(keyword, part, eventType, type, textFormat))
    return comments


def main(keyword: str, part: str, eventType: str, type: str, textFormat: str, num: int):
    t0: float = time.perf_counter()
    # create the asyncio loop
    loop: AbstractEventLoop = asyncio.get_event_loop()
    data = Queue()
    comments = Queue()
    task: Future = asyncio.gather(get_videos(k=keyword, part=part, eventType=eventType, type=type, data=data),
                                  get_video_comments_multiples(num=num, textFormat=textFormat, data=data, comments=comments),
                                  write_to_file('../comments.csv', comments=comments))
    loop.run_until_complete(task)
    t1: float = time.perf_counter()
    print(f"Done in {t1 - t0}")


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    main(keyword='David Goggins', part='id, snippet', eventType='completed', type='video', textFormat='plainText', num=4)
