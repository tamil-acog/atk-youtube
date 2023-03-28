import bisect
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi


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


def data(parsed_time: List, parsed_title: List, video_code: str, method: str = None) -> List:

    parsed_time_in_seconds = []
    if method == "description":
        for i in parsed_time:
            parsed_time_in_seconds.append(get_sec(i))
    else:
        parsed_time_in_seconds = parsed_time

    start, text = get_transcripts(video_code)

    indexes: List = []
    for j in parsed_time_in_seconds:
        indexes.append(find_lt(start, j))

    counter = -1
    text.insert(-1, "\n\n\n")
    for i in indexes[::-1]:

        if i == 0:
            text.insert(0, "\n\n")
            text.insert(0, parsed_title[0])
        else:
            text.insert(i-1, "\n\n")
            text.insert(i-1, parsed_title[counter])
            text.insert(i-1, "\n\n\n")
            counter -= 1
    return start, text