import bisect
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime


def get_sec(time_str):
    """Get seconds from time."""
    if len(time_str.split(':')) == 3:
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
    else:
        m, s = time_str.split(':')
        return int(m) * 60 + int(s)


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







