from bs4 import BeautifulSoup

# HTML content
html = """
<html>
  <head>
    <title>Example Page</title>
  </head>
  <body>
    <p>This is a paragraph.</p>

    This line does not contain any tags.

    <ul>
      <li>Item 1</li>
      <li>Item 2</li>
    </ul>
  </body>
</html>
"""

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Filter out lines that do not contain any tags
lines_with_tags = [line for line in soup.stripped_strings if len(soup.new_tag("p", string=line).find_all()) > 0]

# Print the filtered lines
for line in lines_with_tags:
    print(line)
