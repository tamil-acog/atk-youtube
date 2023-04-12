from atk_youtube_transcript.data_parser import DataParser
from atk_youtube_transcript.prompt import chapter_prompt, general_prompt
from atk_youtube_transcript.transcription_service import TranscriptionService
from atk_youtube_transcript.utils import html_parser
from langchain.llms import OpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import YoutubeLoader
from langchain.docstore.document import Document
import yaml
from typing import List
import pathlib
import os
import warnings

warnings.filterwarnings("ignore")


class Transcript:
    def __init__(self, video_code: str):
        self.llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.video_code = video_code
        self.chapter_prompt: str = chapter_prompt
        self.general_prompt: str = general_prompt
        self.main_dir = pathlib.Path(__file__).parent.resolve()
        self.chapters_css = os.path.join(self.main_dir, "chapters_style.css")
        self.plain_css = os.path.join(self.main_dir, "plain_style.css")
        self.yaml_file = os.path.join(self.main_dir, "config.yaml")
        self.transcription_service = TranscriptionService(self.video_code)
        self.video_title = self.transcription_service.get_video_title()
        with open(self.yaml_file, "r") as f:
            self.config = yaml.safe_load(f)

    def transcript_with_chapters(self, parsed_time: List, parsed_title: List, parsed_images_url: List) -> str:
        print(f"There are total {len(parsed_title)} chapters")
        print(f"Usually it takes around 5-8 mins for a 40 mins video")
        start, text = DataParser.data(parsed_time=parsed_time, parsed_title=parsed_title, video_code=self.video_code)
        file_name = str(self.video_title) + "**" + str(self.video_code) + ".html"
        with open(file_name, "w") as file:
            with open(self.chapters_css, "r") as f:
                for line in f:
                    file.write(line)
            video_link: str = self.config["VIDEO_LINK"]
            video_link_format: str = video_link.format(code=self.video_code, title=self.video_title)
            file.write(video_link_format)

        title_time = 0
        match_index = 0
        counter = 0
        for i in range(len(text)):
            if start[i] == "\n\n":
                title_time = i + 1
            if text[i] == "\n\n\n":
                chunked_text = text[match_index:i]
                chunk = " ".join(chunked_text)
                image_link: str = self.config["IMAGE_LINK"]
                image_prompt: str = f"\nImage link to be added: {image_link.format(url=parsed_images_url[counter])}"
                print(len(parsed_images_url))
                title_link: str = self.config["TITLE_LINK"]
                link_prompt: str = f"\nLink to be added in the title: " \
                                   f"{title_link.format(code=self.video_code, time=start[title_time])}"
                new_prompt = self.chapter_prompt + "\n" + image_prompt + "\n" + link_prompt + "\n\n" + chunk
                response: str = self.llm(new_prompt)
                final_response: str = html_parser(response)
                with open(file_name, "a+") as file:
                    file.write(f"\n\n{final_response}")
                    file.write(f"</div>")

                    counter += 1
                match_index = i + 1
                print(f"Punctuated transcription completed for chapters: {counter}")
            return os.path.join(self.main_dir, file_name)

    def plain_transcript(self) -> str:
        print("Your video don't contain chapters or titles in the description."
                     "So ChatGPT itself is going to add titles for your video")
        print(f"Usually it takes around 5-8 mins for a 40 mins video")
        loader = YoutubeLoader.from_youtube_channel(f"https://www.youtube.com/watch?v={self.video_code}")
        transcripts: List[Document] = loader.load()
        doc: Document = transcripts[0]
        text_splitter = TokenTextSplitter(
            chunk_size=1300, chunk_overlap=0)
        texts = text_splitter.split_text(doc.page_content)
        docs = [Document(page_content=t) for t in texts]
        file_name = str(self.video_title) + "**" + str(self.video_code) + ".html"
        with open(file_name, "w") as file:
            with open(self.plain_css, "r") as f:
                for line in f:
                    file.write(line)
            video_link: str = self.config["VIDEO_LINK"]
            video_link_format: str = video_link.format(code=self.video_code, title=self.video_title)
            file.write(video_link_format)

        for d in docs:
            prompt: str = self.general_prompt + "\n\n" + \
                          d.page_content.replace('[Music]', '')
            response: str = self.llm(prompt)
            final_response: str = html_parser(response)
        with open(file_name, "a+") as file:
            file.write(f"\n{final_response}")
        return os.path.join(self.main_dir, file_name)

    # @jit(target_backend='cuda')
    def whisper_transcript(self) -> str:
        print("Your video do not have captions. So an Audio-to-Speech Model"
                     " will generate the transcripts for you.")
        print(f"Usually it takes around 20 mins for a 40 mins video if it does not contain captions")
        start, texts = DataParser.whisper_data(video_code=self.video_code, video_title=self.video_title)
        transcript = " ".join(texts).strip(" ")
        doc: Document = Document(page_content=transcript)
        text_splitter = TokenTextSplitter(
            chunk_size=1300, chunk_overlap=0)
        texts = text_splitter.split_text(doc.page_content)
        docs = [Document(page_content=t) for t in texts]
        file_name = str(self.video_title) + "**" + str(self.video_code) + ".html"
        with open(file_name, "w") as file:
            with open(self.plain_css, "r") as f:
                for line in f:
                    file.write(line)
            video_link: str = self.config["VIDEO_LINK"]
            video_link_format: str = video_link.format(code=self.video_code, title=self.video_title)
            file.write(video_link_format)

        for d in docs:
            prompt: str = self.general_prompt + "\n\n" + \
                          d.page_content.replace('[Music]', '')
            response: str = self.llm(prompt)
            final_response: str = html_parser(response)
            with open(file_name, "a+") as file:
                file.write(f"\n\n{final_response}")
        return os.path.join(self.main_dir, file_name)

