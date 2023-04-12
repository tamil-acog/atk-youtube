import logging

from atk_youtube_transcript.transcript import Transcript
from atk_youtube_transcript.data_parser import DataParser
from atk_youtube_transcript.transcription_service import TranscriptionService
import typer
import requests

app = typer.Typer()


@app.command()
def transcript(video_code: str):
    do_transcript = Transcript(video_code)
    transcription_service = TranscriptionService(video_code)
    if transcription_service.has_chapters():
        api_chapters_response: requests.Response = requests.get(f'https://yt.lemnoslife.com/videos?part='
                                                                f'chapters&id={video_code}')
        parsed_time, parsed_title, parsed_images_url = DataParser.chapters_parser(api_chapters_response)
        if len(parsed_time) != 0:
            do_transcript.transcript_with_chapters(parsed_time, parsed_title, parsed_images_url)
        else:
            do_transcript.plain_transcript()
    else:
        try:
            do_transcript.whisper_transcript()
        except Exception as err:
            logging.info(err)
    return True


def main() -> None:
    app()
