from atk_youtube_transcript.data_parser import data, whisper_data
from atk_youtube_transcript.prompt import chapter_prompt, general_prompt
from atk_youtube_transcript.utils import get_video_title
from langchain.llms import OpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import YoutubeLoader
from langchain.docstore.document import Document
from numba import jit, cuda
from typing import List
import pathlib
import os
import logging
import yaml

import warnings

warnings.filterwarnings("ignore")
logging.basicConfig(level='INFO')


class Transcript:
    def __init__(self, video_code: str):
        self.llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.video_code = video_code
        self.chapter_prompt: str = chapter_prompt
        self.general_prompt: str = general_prompt
        self.main_dir = pathlib.Path(__file__).parent.resolve()
        self.css_file = os.path.join(self.main_dir, "style.css")
        self.config_file = os.path.join(self.main_dir, "config.yaml")
        self.video_title = get_video_title(self.video_code)


    def transcript_with_chapters(self, parsed_time: List, parsed_title: List, parsed_images_url: List, outfile: str) -> None:

        logging.info(f"There are total {len(parsed_title)} chapters"
                     "\nUsually it takes around 5-8 mins for a 40 mins video")

        start, text = data(parsed_time=parsed_time, parsed_title=parsed_title, video_code=self.video_code)

        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)

        with open(str(outfile) + ".html", "w") as file:
            video_link: str = config["VIDEO_LINK"]
            video_link_format: str = video_link.format(code=self.video_code, title=self.video_title)
            file.write(video_link_format)
            file.write(f"<head><link rel=\"stylesheet\" href=\"{self.css_file}\"></head>")

        match_index = 0
        counter = 0
        for i in range(len(text)):
            if text[i] == "\n\n\n":
                chunk = " ".join(text[match_index:i])
                print(chunk)

                image_link: str = config["IMAGE_LINK"]
                image_prompt: str = f"\nImage link to be added: {image_link.format(url= parsed_images_url[counter])}"
                title_link: str = config["TITLE_LINK"]
                link_prompt: str = f"\nLink to be added in the title: {title_link.format(code= self.video_code,time= start[match_index])}"

                new_prompt = self.chapter_prompt + "\n" + image_prompt + "\n" + link_prompt + "\n\n" + chunk
                print(new_prompt)

                response: str = self.llm(new_prompt)
                print(response)
                with open(str(outfile) + ".html", "a+") as file:
                    file.write(f"\n\n{response}")
                    counter += 1
                match_index = i + 1

                logging.info(f"Punctuated transcription completed for chapters: {counter}")
        return

    def plain_transcript(self, outfile: str) -> None:

        logging.info("Your video don't contain chapters or titles in the description."
                     "So ChatGPT itself is going to add titles for your video."
                     "Usually it takes around 5-8 mins for a 40 mins video")


        loader = YoutubeLoader.from_youtube_channel(f"https://www.youtube.com/watch?v={self.video_code}")
        transcripts: List[Document] = loader.load()
        doc: Document = transcripts[0]
        text_splitter = TokenTextSplitter(
            chunk_size=1300, chunk_overlap=0)
        texts = text_splitter.split_text(doc.page_content)
        docs = [Document(page_content=t) for t in texts]

        with open(str(outfile) + ".html", "w") as file:
            file.write(f"<h1 style=\"text-align: center;\"><a href=\"https://www.youtube.com/watch?v={self.video_code}"
                       f"\"><strong>{self.video_title}</strong></a></h1>")
        for d in docs:
            prompt: str = self.general_prompt + "\n\n" + \
                          d.page_content.replace('[Music]', '')
            response: str = self.llm(prompt)
            with open(outfile + ".html", 'a+') as f:
                f.write(f"\n{response}")
        return

    # @jit(target_backend='cuda')
    def whisper_transcript(self, outfile: str) -> None:
        logging.info("Your video do not have captions. So an Audio-to-Speech Model"
                     " will generate the transcripts for you.")
        logging.info(f"Usually it takes around 20 mins for a 40 mins video if it does not contain captions")
        start, texts = whisper_data(video_code=self.video_code, outfile=outfile)
        doc: Document = texts
        text_splitter = TokenTextSplitter(
            chunk_size=1300, chunk_overlap=0)
        texts = text_splitter.split_text(doc.page_content)
        docs = [Document(page_content=t) for t in texts]
        with open(str(outfile) + ".html", "w") as file:
            file.write(f"<h1 style=\"text-align: center;\"><a href=\"https://www.youtube.com/watch?v={self.video_code}"
                       f"\"><strong>{self.video_title}</strong></a></h1>")
        for d in docs:
            prompt: str = self.general_prompt + "\n\n" + \
                          d.page_content.replace('[Music]', '')
            response: str = self.llm(prompt)
            with open(outfile + ".html", 'a+') as f:
                f.write(f"\n{response}")
        return






