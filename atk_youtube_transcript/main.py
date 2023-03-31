import logging

from atk_youtube_transcript.transcript import Transcript
from atk_youtube_transcript.data_parser import chapters_parser
from atk_youtube_transcript.utils import get_transcripts
import typer


app = typer.Typer()


@app.command()
def transcript(video_code: str, outfile: str):
    do_transcript = Transcript(video_code)

    try:
        _, _ = get_transcripts(video_code)
        parsed_time, parsed_title, parsed_images_url = chapters_parser(video_code)

        if len(parsed_time) != 0:
            do_transcript.transcript_with_chapters(parsed_time, parsed_title, parsed_images_url, outfile)
        else:
            do_transcript.plain_transcript(outfile)

    except Exception as err:
        logging.info(err)
        try:
            do_transcript.whisper_transcript(outfile)
        except Exception as err:
            logging.info(err)


def main() -> None:
    app()
    