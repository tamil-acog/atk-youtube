from atk_youtube_transcript.data_parser import DataParser
from atk_youtube_transcript.prompt import chapter_prompt, general_prompt
from atk_youtube_transcript.transcription_service import TranscriptionService
from langchain.llms import OpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import YoutubeLoader
from langchain.docstore.document import Document
import yaml
from numba import jit, cuda
from typing import List
import pathlib
import os
import logging

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
        self.yaml_file = os.path.join(self.main_dir, "config.yaml")
        self.transcription_service = TranscriptionService(self.video_code)
        self.video_title = self.transcription_service.get_video_title()
        with open(self.yaml_file, "r") as f:
            self.config = yaml.safe_load(f)

    def transcript_with_chapters(self, parsed_time: List, parsed_title: List, parsed_images_url: List, outfile: str) -> None:
        logging.info(f"There are total {len(parsed_title)} chapters")
        logging.info(f"Usually it takes around 5-8 mins for a 40 mins video")
        start, text = DataParser.data(parsed_time=parsed_time, parsed_title=parsed_title, video_code=self.video_code)
        with open("test.py", "w") as d:
            d.write(str(text))
            d.write(str(start))

        with open(str(outfile) + ".html", "w") as file:
            video_link: str = self.config["VIDEO_LINK"]
            video_link_format: str = video_link.format(code=self.video_code, title=self.video_title)
            file.write(video_link_format)
            #file.write(f"<head><link rel=\"stylesheet\" href=\"{self.css_file}\"></head>")
            file.write(f"<head><link rel=\"stylesheet\" href=\"style.css\"></head>")

        title_time = 0
        match_index = 0
        counter = 0
        for i in range(len(text)):
            if start[i] == "\n\n":
                title_time = i + 1
            if text[i] == "\n\n\n":
                chunked_text = text[match_index:i]
                chunk = " ".join(chunked_text)
                print(chunk)
                image_link: str = self.config["IMAGE_LINK"]
                image_prompt: str = f"\nImage link to be added: {image_link.format(url=parsed_images_url[counter])}"
                title_link: str = self.config["TITLE_LINK"]
                link_prompt: str = f"\nLink to be added in the title: " \
                                   f"{title_link.format(code=self.video_code, time=start[title_time])}"
                new_prompt = self.chapter_prompt + "\n" + image_prompt + "\n" + link_prompt + "\n\n" + chunk
                print(new_prompt)
                response: str = self.llm(new_prompt)
                print(response, "hi")
                with open(str(outfile) + ".html", "a+") as file:
                    file.write(f"\n\n{response}")
                    counter += 1
                match_index = i + 1
                logging.info(f"Punctuated transcription completed for chapters: {counter}")
        return

    def plain_transcript(self, outfile: str) -> None:
        logging.info("Your video don't contain chapters or titles in the description."
                     "So ChatGPT itself is going to add titles for your video")
        logging.info(f"Usually it takes around 5-8 mins for a 40 mins video")
        loader = YoutubeLoader.from_youtube_channel(f"https://www.youtube.com/watch?v={self.video_code}")
        transcripts: List[Document] = loader.load()
        doc: Document = transcripts[0]
        text_splitter = TokenTextSplitter(
            chunk_size=1300, chunk_overlap=0)
        texts = text_splitter.split_text(doc.page_content)
        docs = [Document(page_content=t) for t in texts]
        with open(str(outfile) + ".html", "w") as file:
            video_link: str = self.config["VIDEO_LINK"]
            video_link_format: str = video_link.format(code=self.video_code, title=self.video_title)
            file.write(video_link_format)
            # file.write(f"<head><link rel=\"stylesheet\" href=\"{self.css_file}\"></head>")
            file.write(f"<head><link rel=\"stylesheet\" href=\"style.css\"></head>")

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
        start, texts = DataParser.whisper_data(video_code=self.video_code, outfile=outfile)
        transcript = " ".join(texts).strip(" ")
        doc: Document = Document(page_content=transcript)
        text_splitter = TokenTextSplitter(
            chunk_size=1300, chunk_overlap=0)
        texts = text_splitter.split_text(doc.page_content)
        docs = [Document(page_content=t) for t in texts]
        with open(str(outfile) + ".html", "w") as file:
            video_link: str = self.config["VIDEO_LINK"]
            video_link_format: str = video_link.format(code=self.video_code, title=self.video_title)
            file.write(video_link_format)
            # file.write(f"<head><link rel=\"stylesheet\" href=\"{self.css_file}\"></head>")
            file.write(f"<head><link rel=\"stylesheet\" href=\"style.css\"></head>")

        for d in docs:
            prompt: str = self.general_prompt + "\n\n" + \
                          d.page_content.replace('[Music]', '')
            response: str = self.llm(prompt)
            with open(outfile + ".html", 'a+') as f:
                f.write(f"\n{response}")
        return






