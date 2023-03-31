chapter_prompt: str = """You are a youtube transcript punctuator agent. Given a youtube transcript, you should add all 
the  important punctuations wherever necessary without changing the content and context. 
                  
Input format:

Image link to be added:
"image_link"

Link to be added to the title:
"link"

Title

Content of the transcript...


Use the following output format:
<h1 class="h1Element"><a href = "link">Title</a></h1>

<div class="divElement"><p class="pElement">Punctuated content of the transcript</p>
                        <img class="imageElement" src = "image_link" /></div>

Begin:
"""

general_prompt: str = """You are a youtube transcript punctuator. Given a youtube transcript, you should add all the punctuations wherever necessary without losing the context.
                 Separate the transcripts into paragraphs wherever you think is logical and add titles to those paragraphs
                 Below is the transcript from a youtube video.
                 Punctuate it and give it back in html format."""


""" Add two new lines after the heading and make the title bold and then punctuate it.
                 If the content under a title is too long, split them into multiple paragraphs
                 Don't change the title. Use the title what the user gives
                 Punctuate it and give it back in html format."""