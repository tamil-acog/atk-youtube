import requests
from typing import List
from atk_youtube_transcript.youtube import YouTube
from atk_youtube_transcript.utils import data
from langchain.docstore.document import Document
import typer
from langchain.text_splitter import TokenTextSplitter
from langchain.llms import OpenAI
from atk_youtube_transcript.prompt import title_prompt, general_prompt
import logging
import traceback
import sys
from langchain.document_loaders import YoutubeLoader
import warnings


warnings.filterwarnings("ignore")
logging.basicConfig(level='INFO')
app = typer.Typer()


@app.command()
def transcript(video_code: str, outfile: str):
    llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
    idx = 0
    prompt: str = title_prompt
    youtube: YouTube = YouTube(video_code)

    api_chapters_response: requests.Response = requests.get(f'https://yt.lemnoslife.com/videos?part='
                                                            f'chapters&id={video_code}')

    parsed_time, parsed_title, parsed_images_url = youtube.from_chapters(api_chapters_response)
    if len(parsed_time) != 0:
        logging.info(f"There are total {len(parsed_title)} chapters")
        logging.info(f"Usually it takes around 5-8 mins for a 40 mins video")
        start, text = data(parsed_time=parsed_time, parsed_title=parsed_title, video_code=video_code, method="chapters")
        counter = 0
        for i in range(len(text)):
            if text[i] == "\n\n\n":
                chunked_text = text[idx:i]
                chunk = " ".join(chunked_text)
                new_prompt = prompt + "\n\n" + chunk
                response: str = llm(new_prompt)
                with open(str(outfile)+".html", "a+") as file:
                    file.write(f"\n\n{response}")
                    file.write(f"\n<img src=\"{parsed_images_url[counter]}\" alt=\"Not Applicable\" />")
                    file.write(f"\n<a href=\"https://www.youtube.com/watch?v={video_code}&t={start[idx]}s\">"
                               f"{chunked_text[0]}</a>\n")
                    counter += 1
                idx = i+1
                logging.info(f"Punctuated transcription completed for chapters: {counter}")
        return
    else:
        api_description_response: requests.Response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part='
                                                                   f'snippet&id={video_code}&'
                                                                   f'key=AIzaSyDQP56aoFMwjJsanu3dfiGXmQEIkb-BzLc')

        parsed_time, parsed_title = youtube.from_description(api_description_response)
        if len(parsed_time) != 0:
            logging.info(f"There are total {len(parsed_title)} titles")
            logging.info(f"Usually it takes around 5-8 mins for a 40 mins video")
            start, text = data(parsed_time=parsed_time, parsed_title=parsed_title, video_code=video_code, method="description")
            counter = 0
            for i in range(len(text)):
                if text[i] == "\n\n\n":
                    chunked_text = text[idx:i]
                    chunk = " ".join(chunked_text)
                    new_prompt = prompt + "\n\n" + chunk
                    response: str = llm(new_prompt)
                    with open(str(outfile)+".html", "a+") as file:
                        file.write(f"\n\n{response}")
                        file.write(f"\n<a href=\"https://www.youtube.com/watch?v={video_code}&t="
                                   f"{start[idx]}s\">{chunked_text[0]}</a>\n")
                    counter += 1
                    idx = i+1
                    logging.info(f"Punctuated transcription completed for chapters: {counter}")
            return
        else:
            try:
                logging.info("Your video don't contain chapters or titles in the description."
                             "So ChatGPT itself is going to add titles for your video")
                logging.info(f"Usually it takes around 5-8 mins for a 40 mins video")
                loader = YoutubeLoader.from_youtube_channel(f"https://www.youtube.com/watch?v={video_code}")
                transcripts: List[Document] = loader.load()
                doc: Document = transcripts[0]
                text_splitter = TokenTextSplitter(
                    chunk_size=1900, chunk_overlap=0)
                texts = text_splitter.split_text(doc.page_content)
                docs = [Document(page_content=t) for t in texts]
                for d in docs:
                    prompt: str = general_prompt + "\n\n" + \
                                  d.page_content.replace('[Music]', '')
                    response: str = llm(prompt)
                    with open(outfile+".html", 'a+') as f:
                        f.write(f"\n{response}")
                return
            except Exception as err:
                traceback.print_exc(file=sys.stdout)
                return


def main() -> None:
    app()
    