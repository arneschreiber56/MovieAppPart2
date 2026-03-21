"""contains the logic to load html_template, process the HTML string and
create the movie app index.html webpage"""
from bs4 import BeautifulSoup

PATH_TEMPLATE = "_static/index_template.html"
PATH_INDEX = "webpage/index.html"
TITLE_PLACEHOLDER = "__TEMPLATE_TITLE__"
GRID_PLACEHOLDER = "__TEMPLATE_MOVIE_GRID__"



def load_index_html_template():
    """loads html_template from the index_template file and returns the template
    as a string if successful and an error message if not"""
    try:
        with open(PATH_TEMPLATE, "r", encoding="utf-8") as txtobj:
            html_template = txtobj.read()
    except OSError as e:
        return None, str(e)
    else:
        return html_template, None


def prepare_title_html(raw_html, app_title):
    """adds a title to the index_html webpage, returns adapted HTML if
    successful, None if not"""
    app_title = app_title.strip()
    if TITLE_PLACEHOLDER in raw_html:
        title_html = raw_html.replace(TITLE_PLACEHOLDER, app_title)
        return title_html, None
    else:
        return None, "error_title_placeholder"


def prepare_movie_grid_html(title_html, html_movie_snippet):
    """adds the movie grid container HTML code to the HTML and returns a
    processed_html string if successful and None if not"""
    if GRID_PLACEHOLDER in title_html:
        processed_html = title_html.replace(
            GRID_PLACEHOLDER, html_movie_snippet
        )
        return processed_html, None
    else:
        return None, "error_grid_placeholder"


def beautify_html(processed_html):
    """beautifies the HTML string for writing into index.html"""
    soup = BeautifulSoup(processed_html, "html.parser")
    pretty_html = soup.prettify(formatter='html')
    beautiful_html = pretty_html.replace("  ", "    ")
    return beautiful_html


def write_index_html(beautiful_html):
    """gets the formatted_html as a string variable and writes it in the index
    html file. Returns None if successful and a error message if not"""
    try:
        with open(PATH_INDEX, "w", encoding="utf-8") as txtobj:
            txtobj.write(beautiful_html)
    except OSError as e:
        return e
    else:
        return None