import bisect
import re
from bs4 import BeautifulSoup


def find_lt(a, x):
    """Find rightmost value less than x"""
    if x == '00:00:00' or x == 0:
        return 0
    i = bisect.bisect_left(a, x)
    if i:
        if a[i] == x:
            return i
        else:
            return i-1

def html_parser(response: str):
    """Removes the lines without html tags."""
    soup = BeautifulSoup(response, 'html.parser')

    for p in soup.find_all('p'):
        p.string = p.get_text(strip=True)

    modified_html = str(soup)

    pattern = re.compile(r'^[^\n<]*$[\n]*', re.MULTILINE)

    modified_response = re.sub(pattern, '', modified_html)

    return modified_response











