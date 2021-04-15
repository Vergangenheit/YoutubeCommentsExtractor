import asyncio
from asyncio import AbstractEventLoop
from aiogoogle import Aiogoogle, GoogleAPI
from aiogoogle.models import Response, Request
import config
from typing import List, Dict, Coroutine, Any
import time


async def get_videos(q: str, part: str, eventType: str, type: str) -> Dict:
    async with Aiogoogle(api_key=config.API_KEY) as aiog:
        youtube: GoogleAPI = await aiog.discover('youtube', 'v3')
        req: Request = youtube.search.list(q=q, part=part, eventType=eventType, type=type)
        res: Dict = await aiog.as_api_key(req)
    videos: List[Dict] = res.get('items')
    # print(videos)

    return videos


async def get_video_comments(videoId: str, textFormat: str) -> List:
    comments: List = []
    async with Aiogoogle(api_key=config.API_KEY) as aiocomments:
        youtube: GoogleAPI = await aiocomments.discover('youtube', 'v3')
        req = youtube.commentThreads.list(videoId=videoId, part='snippet', textFormat=textFormat)
        results: Dict = await aiocomments.as_api_key(req)

    for item in results.get('items'):
        comment: str = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

    return comments


async def get_video_comments_multiples(videoId: str, textFormat: str):
    comments: List = []
    async with Aiogoogle(api_key=config.API_KEY) as aiocomments:
        youtube: GoogleAPI = await aiocomments.discover('youtube', 'v3')
        req = youtube.commentThreads.list(videoId=videoId, part='snippet', textFormat=textFormat)
        results: Coroutine[Dict] = await aiocomments.as_api_key(req)
        while results:
            for item in results.get('items'):
                comment: str = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)
            if 'nextPageToken' in results:
                pageToken = results['nextPageToken']
                req = youtube.commentThreads.list(videoId=videoId, part='snippet', textFormat=textFormat,
                                                  pageToken=pageToken)
                results: Dict = await aiocomments.as_api_key(req)
            else:
                break

    print(comments)


# def main(**kwargs):
#     # create loop
#     t0: float = time.perf_counter()
#     loop: AbstractEventLoop = asyncio.get_event_loop()
#     loop.run_until_complete(search_videos_comments_by_keyword(loop, **kwargs))
#     t1: float = time.perf_counter()
#     print(f"Done in {t1 - t0}")


if __name__ == "__main__":
    # asyncio.run(get_videos(q='David Goggins', part='id, snippet', eventType='completed',
    #                                   type='video'))
    asyncio.run(get_video_comments_multiples(videoId='5tSTk1083VY', textFormat='plainText'))
    # main(q='David Goggins', part='id, snippet', eventType='completed', type='video', textFormat='plainText')