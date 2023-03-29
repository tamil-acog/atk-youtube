from atk_youtube_transcript.data_parser import data, whisper_data
from atk_youtube_transcript.prompt import title_prompt, general_prompt
from langchain.llms import OpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import YoutubeLoader
from langchain.docstore.document import Document
from numba import jit, cuda
from typing import List
import logging

import warnings



warnings.filterwarnings("ignore")
logging.basicConfig(level='INFO')


class Transcript:
    def __init__(self):
        self.llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.title_prompt: str = title_prompt
        self.general_prompt: str = general_prompt
        pass

    def transcript_with_chapters(self, parsed_time: List, parsed_title: List, parsed_images_url: List, video_code: str, outfile) -> None:
        logging.info(f"There are total {len(parsed_title)} chapters")
        logging.info(f"Usually it takes around 5-8 mins for a 40 mins video")
        start, text = data(parsed_time=parsed_time, parsed_title=parsed_title, video_code=video_code, method="chapters")
        counter = 0
        for i in range(len(text)):
            if text[i] == "\n\n\n":
                chunked_text = text[idx:i]
                chunk = " ".join(chunked_text)
                new_prompt = self.title_prompt + "\n\n" + chunk
                response: str = self.llm(new_prompt)
                with open(str(outfile) + ".html", "a+") as file:
                    file.write(f"\n\n{response}")
                    file.write(f"\n<img src=\"{parsed_images_url[counter]}\" alt=\"Not Applicable\" />")
                    file.write(f"\n<a href=\"https://www.youtube.com/watch?v={video_code}&t={start[idx]}s\">"
                               f"{chunked_text[0]}</a>\n")
                    counter += 1
                idx = i + 1
                logging.info(f"Punctuated transcription completed for chapters: {counter}")
        return

    def transcript_with_description(self, parsed_time, parsed_title, video_code, outfile) -> None:
        logging.info(f"There are total {len(parsed_title)} titles")
        logging.info(f"Usually it takes around 5-8 mins for a 40 mins video")
        start, text = data(parsed_time=parsed_time, parsed_title=parsed_title, video_code=video_code,
                           method="description")
        counter = 0
        for i in range(len(text)):
            if text[i] == "\n\n\n":
                chunked_text = text[idx:i]
                chunk = " ".join(chunked_text)
                new_prompt = self.title_prompt + "\n\n" + chunk
                response: str = self.llm(new_prompt)
                with open(str(outfile) + ".html", "a+") as file:
                    file.write(f"\n\n{response}")
                    file.write(f"\n<a href=\"https://www.youtube.com/watch?v={video_code}&t="
                               f"{start[idx]}s\">{chunked_text[0]}</a>\n")
                counter += 1
                idx = i + 1
                logging.info(f"Punctuated transcription completed for chapters: {counter}")
        return

    def plain_transcript(self, video_code: str, outfile: str) -> None:
        logging.info("Your video don't contain chapters or titles in the description."
                     "So ChatGPT itself is going to add titles for your video")
        logging.info(f"Usually it takes around 5-8 mins for a 40 mins video")
        loader = YoutubeLoader.from_youtube_channel(f"https://www.youtube.com/watch?v={video_code}")
        transcripts: List[Document] = loader.load()
        doc: Document = transcripts[0]
        text_splitter = TokenTextSplitter(
            chunk_size=1300, chunk_overlap=0)
        texts = text_splitter.split_text(doc.page_content)
        docs = [Document(page_content=t) for t in texts]
        for d in docs:
            prompt: str = self.general_prompt + "\n\n" + \
                          d.page_content.replace('[Music]', '')
            response: str = self.llm(prompt)
            with open(outfile + ".html", 'a+') as f:
                f.write(f"\n{response}")
        return

    @jit(target_backend='cuda')
    def whisper_transcript(self, video_code: str, outfile: str) -> None:
        logging.info("Your video do not have captions. So an Audio-to-Speech Model"
                     " will generate the transcripts for you.")
        logging.info(f"Usually it takes around 20 mins for a 40 mins video if it does not contain captions")
        start, texts = whisper_data(video_code=video_code, outfile=outfile)
        doc: Document = texts
        text_splitter = TokenTextSplitter(
            chunk_size=1300, chunk_overlap=0)
        texts = text_splitter.split_text(doc.page_content)
        docs = [Document(page_content=t) for t in texts]
        for d in docs:
            prompt: str = self.general_prompt + "\n\n" + \
                          d.page_content.replace('[Music]', '')
            response: str = self.llm(prompt)
            with open(outfile + ".html", 'a+') as f:
                f.write(f"\n{response}")
        return






