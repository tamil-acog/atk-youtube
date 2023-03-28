import requests
from atk_youtube_transcript.youtube import YouTube
from atk_youtube_transcript.utils import data
import typer
from langchain.chat_models import ChatOpenAI


app = typer.Typer()


@app.command()
def transcript(video_code: str, outfile: str):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    idx = 0
    prompt: str = """You are a youtube transcript punctuator. Given a youtube transcript, you should add all the punctuations wherever necessary without losing the context.
    Below is the transcript from a youtube video.
    Punctuate it and give it back in html format.

    The first line is the title. Add two new lines after the heading and make the title bold and then punctuate it."""
    youtube = YouTube(video_code)

    api_chapters_response: requests.Response = requests.get(f'https://yt.lemnoslife.com/videos?part='
                                                            f'chapters&id={video_code}')
    
    if api_chapters_response.ok:
        parsed_time, parsed_title, parsed_images_url = youtube.from_chapters(api_chapters_response)
        start, text = data(parsed_time=parsed_time, parsed_title=parsed_title, video_code=video_code, method="chapters")
        counter = 0
        for i in range(len(text)):
            if text[i] == "\n\n\n":
                chunked_text = text[idx:i]
                chunk = " ".join(chunked_text)
                new_prompt = prompt + "\n\n" + chunk
                print(new_prompt)
                response: str = llm(new_prompt)
                print(response)
                with open(str(outfile)+".html", "a+") as file:
                    file.write(f"\n\n{response}")
                    file.write(f"\n<img src=\"{parsed_images_url[counter]}\" alt=\"Not Applicable\" />")
                    file.write(f"\n<a href=\"https://www.youtube.com/watch?v={video_code}&t={start[idx]}s\">"
                               f"{chunked_text[0]}</a>\n")
                    counter += 1
                idx = i+1
    else:
        api_description_response: requests.Response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part='
                                                                   f'snippet&id={video_code}&'
                                                                   f'key=AIzaSyDQP56aoFMwjJsanu3dfiGXmQEIkb-BzLc')
        if api_description_response.ok:
            parsed_time, parsed_title = youtube.from_description(api_description_response)
            start, text = data(parsed_time=parsed_time, parsed_title=parsed_title, video_code=video_code, method="description")

            for i in range(len(text)):
                if text[i] == "\n\n\n":
                    chunked_text = text[idx:i]
                    chunk = " ".join(chunked_text)
                    new_prompt = prompt + "\n\n" + chunk
                    print(new_prompt)
                    response: str = llm(new_prompt)
                    print(response)
                    with open(str(outfile)+".html", "a+") as file:
                        file.write(f"\n\n{response}")
                        file.write(f"\n<a href=\"https://www.youtube.com/watch?v={video_code}&t="
                                   f"{start[idx]}s\">{chunked_text[0]}</a>\n")
                    idx = i+1


def main() -> None:
    app()
    