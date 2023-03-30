import bisect
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
import requests

def get_transcripts(video_code: str) -> List[str]:
    start: List = []
    text: List = []

    # Get the start time and text of closed captions from transcript API 
    trans = YouTubeTranscriptApi.get_transcript(video_code)
    for content in trans:
        start.append(content['start'])
        text.append(content['text'])

    return start, text


def find_lt(a, x):
    """Find rightmost value less than x"""
    if x == '00:00:00' or x == 0:
        return 0
    i = bisect.bisect_left(a, x)
    if i:
        if a[i] == x:
            return i
        else:
            return i-1


def get_video_title(video_code: str) -> str:
    api_description_response: requests.Response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part='
                                                               f'snippet&id={video_code}&'
                                                               f'key=AIzaSyDQP56aoFMwjJsanu3dfiGXmQEIkb-BzLc')

    api_response = api_description_response.json()
    video_title: str = api_response['items'][0]['snippet']['title']
    return video_title







