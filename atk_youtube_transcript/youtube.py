import re
from typing import List


class YouTube:
    def __init__(self, video_code:str) -> None:
        self.video_code: str = video_code
        self.parsed_time: List = []
        self.parsed_title: List = []
        self.parsed_images_url: List = []
        
    def from_description(self, api_response_object: object) -> list[str]:
        """Given a video link, get the times from descriptions"""
        description: str

        # Get the description from the API response
        api_response: object = api_response_object.json()
        description = api_response['items'][0]['snippet']['description']

        # Parse the time from descrption
        pattern_time: str = r"\d\d?:\d\d?"
        self.parsed_time = re.findall(pattern_time, description)
        
        # Parse the title from description
        pattern_title: str = r"\d{2}:\d{2}([\s\S]*?)\n"
        self.parsed_title: List = re.findall(pattern_title, description)
        final_pattern = r'(?:\d{2}:\d{2})(.*?)(?=\d{2}:\d{2}|$)'
        final_matches = re.findall(final_pattern, description)
        self.parsed_title.extend(final_matches)
        
        return self.parsed_time, self.parsed_title
    
    def from_chapters(self, api_response_object: object) -> List[str]:

        api_response = api_response_object.json()
        
        number_of_titles:int = len(api_response['items'][0]['chapters']['chapters'])
        
        for i in range(0,number_of_titles):
            self.parsed_title.append(api_response['items'][0]['chapters']['chapters'][i]['title'])
            self.parsed_time.append(api_response['items'][0]['chapters']['chapters'][i]['time'])
            self.parsed_images_url.append(api_response['items'][0]['chapters']['chapters'][i]['thumbnails'][1]['url'])

        
        return self.parsed_time, self.parsed_title, self.parsed_images_url

