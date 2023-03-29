from atk_youtube_transcript.transcript import Transcript
from atk_youtube_transcript.data_parser import chapters_parser, description_parser
from atk_youtube_transcript.utils import get_transcripts
import typer
import requests

app = typer.Typer()


@app.command()
def transcript(video_code: str, outfile: str):
    do_transcript = Transcript()
    try:
        _, _ = get_transcripts(video_code)
        api_chapters_response: requests.Response = requests.get(f'https://yt.lemnoslife.com/videos?part='
                                                                f'chapters&id={video_code}')
        parsed_time, parsed_title, parsed_images_url = chapters_parser(api_chapters_response)
        print(parsed_time, parsed_title)
        if len(parsed_time) != 0:
            do_transcript.transcript_with_chapters(parsed_time, parsed_title, parsed_images_url, video_code, outfile)
        else:
            api_description_response: requests.Response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part='
                                                                       f'snippet&id={video_code}&'
                                                                       f'key=AIzaSyDQP56aoFMwjJsanu3dfiGXmQEIkb-BzLc')

            parsed_time, parsed_title = description_parser(api_description_response)
            if len(parsed_time) != 0:
                do_transcript.transcript_with_description(parsed_time, parsed_title, video_code, outfile)
            else:
                do_transcript.plain_transcript(video_code, outfile)

    except Exception as err:
        do_transcript.whisper_transcript()


def main() -> None:
    app()
    