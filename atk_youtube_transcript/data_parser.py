import re
from typing import List
from atk_youtube_transcript.utils import get_transcripts, find_lt
import pytube
import whisper
from datetime import datetime


def chapters_parser(api_response_object: object) -> List[str]:
    api_response = api_response_object.json()
    parsed_time: List = []
    parsed_title: List = []
    parsed_images_url: List = []

    number_of_titles: int = len(api_response['items'][0]['chapters']['chapters'])
    for i in range(0, number_of_titles):
        parsed_time.append(api_response['items'][0]['chapters']['chapters'][i]['time'])
        parsed_title.append(api_response['items'][0]['chapters']['chapters'][i]['title'])
        parsed_images_url.append(api_response['items'][0]['chapters']['chapters'][i]['thumbnails'][1]['url'])

    return parsed_time, parsed_title, parsed_images_url


def data(parsed_time: List, parsed_title: List, video_code: str, method: str = None) -> List:

    parsed_time_in_seconds: List = parsed_time

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


def whisper_data(video_code: str, outfile: str) -> List:
    url = f"https://www.youtube.com/watch?v={video_code}"
    video = pytube.YouTube(url)
    audio = video.streams.get_audio_only()
    audio.download(filename=outfile + '.mp3')
    model = whisper.load_model("small")
    transcription = model.transcribe(outfile+'.mp3')
    res = transcription['segments']

    texts = []
    start_times = []

    for segment in res:
        text = segment['text']
        start = segment['start']

        # Convert the starting time to a datetime object
        start_datetime = datetime.fromtimestamp(start)

        # Format the starting time as a string in the format "00:00:00"
        formatted_start_time = start_datetime.strftime('%H:%M:%S')

        texts.append("".join(text))
        start_times.append(formatted_start_time)

    return start_times, texts


