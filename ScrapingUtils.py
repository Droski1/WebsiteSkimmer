import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import requests
import time
import tqdm
import SheetUtils

'''

Gabriels Rapture Part III 2022


'''


def GetHTML(URL):
    response = requests.get(URL)
    return response.content

def GetMovieInfo(movie = "the-super-mario-bros-movie-2023-42661"):
    soup = BeautifulSoup(GetHTML('https://nepu.to/movie/' + movie), 'html.parser')
    ### GETS VIEW COUNT ###

    # Find the div element with class "view-text"
    div = soup.find('div', class_='view-text')

    # Extract the text within the div and remove leading/trailing whitespace
    view_count = div.get_text(strip=True)

    ### Gathers things like, IMDB Score, Country, Genre, Duration, Relase, and Overview, which could be thrown out later if its seen to be too innefficent on space ###

    # Find all div elements with class "video-attr"
    video_attr_divs = soup.find_all('div', class_='video-attr')

    # Iterate over the video_attr_divs and extract the attributes
    attributes = []
    for video_attr_div in video_attr_divs:
        attr_div = video_attr_div.find('div', class_='attr')
        text_div = video_attr_div.find('div', class_='text')
        if attr_div and text_div:
            attribute = {
                'attribute_name': attr_div.get_text(strip=True),
                'attribute_value': text_div.get_text(strip=True)
            }
            attributes.append(attribute)

    # Print the extracted attributes
    for attribute in attributes:
        print(attribute)

    print(view_count)
    div_tag = soup.find('div', class_='play-btn')
    data_id = div_tag['data-id']
    print(data_id)

def GetTotalMovies(url = 'https://nepu.to/movies?filter={"sorting":"newest"}&page=1'):

    # Moved Soup object into here so its easier, and also more compact, not sure how itll effect anything else though

    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    # Selects that because that is what tells us how many movies there are in theory.
    # IF THIS CHANGES, REDO THIS
    text = str(soup.select('div[class*="text-muted"][class*="text-12"]')[0])

    # Deletes the first part of the code, so it only selects the last bits
    text = text[32:]

    # Strips everything after the word 'contains'
    text = text[:text.find("contains")]

    # What should result is just the integer, if not well fuck
    return int(text)

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from bs4 import BeautifulSoup

def GetMovieList(url='https://nepu.to/movies?filter={"sorting":"newest"}&page=',
                 max_pages=0,
                 workers=16):
    urls = []

    if max_pages <= 0:
        # Assuming GetTotalMovies() is a valid function
        max_pages = (GetTotalMovies() / 20).__ceil__()

    def SurfPageForMovies(url):
        soup = BeautifulSoup(GetHTML(url), 'html.parser')
        movies_found = []
        flipper = True

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and 'movie/' in href and flipper:
                movies_found.append(href[22:])
                flipper = False
            else:
                flipper = True

        return movies_found

    for i in range(max_pages):
        urls.append(url + str(i))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(SurfPageForMovies, url) for url in urls]

        progress_bar = tqdm(total=len(futures), unit="task")

        results = []
        for future in futures:
            result = future.result()
            results.append(result)
            progress_bar.update(1)

        progress_bar.close()

    return [string for sublist in results for string in sublist]



def GetMovieFromInternalID(id=000000):
    # Max = 265572
    session = requests.Session()
    start_time = time.time()
    response = session.post("https://nepu.to/ajax/embed", data={"id": id})
    end_time = time.time()
    elapsed_time_ms = (end_time - start_time) * 1000
    elapsed_time_ms.__round__()

    video = response.text.split('"')[5]
    preview = response.text.split('"')[7]
    return video, preview, elapsed_time_ms

'''
print(GetMovieInfo())


MovieSheet = SheetUtils.getSpreadSheet().sheet1
movies = GetMovieList(max_pages=32, workers=16)

# Define the target column range
column_range = f'A2:A{len(movies)+1}'

# Update the column with the array of values
MovieSheet.update(column_range, [[value] for value in movies])

movies.remove("meme-lord-of-the-rings-but-every-time-sam-takes-a-step-towards-mordor-he-says-one-more-step-i-ll-be-the-farthest-away-i-ve-from-home-i-ve-ever-been-2001-42339")

print(movies)
'''