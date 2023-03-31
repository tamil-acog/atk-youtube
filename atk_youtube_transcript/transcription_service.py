from youtube_transcript_api import YouTubeTranscriptApi
from typing import List
import requests


class TranscriptionService:
    def __init__(self, video_code: str):
        self.video_code = video_code
        pass

    def has_chapters(self) -> bool:
        try:
            _, _ = self.get_transcription()
            return True
        except Exception as err:
            return False

    def get_transcription(self) -> tuple[List, List]:
        start: List = []
        text: List = []

        # Get the start time and text of closed captions from transcript API
        trans = YouTubeTranscriptApi.get_transcript(self.video_code)
        for content in trans:
            start.append(content['start'])
            text.append(content['text'])

        return start, text

    def get_video_title(self) -> str:
        api_description_response: requests.Response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part='
                                                                   f'snippet&id={self.video_code}&'
                                                                   f'key=AIzaSyDQP56aoFMwjJsanu3dfiGXmQEIkb-BzLc')

        api_response = api_description_response.json()
        video_title: str = api_response['items'][0]['snippet']['title']
        return video_title
