import ScrapingUtils
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import requests
import time
import tqdm
import SheetUtils
import gspread
from datetime import datetime
import concurrent.futures
import requests
import time
from datetime import datetime
import tqdm
import Utils

import atexit

def save_data():
    # Call the update_column function
    SheetUtils.update_column(spreadsheet, 'A', [item[0] for item in dataBase])             # Updated Date
    SheetUtils.update_column(spreadsheet, 'I', [item[2][55:][:-4] for item in dataBase])   # Preview
    SheetUtils.update_column(spreadsheet, 'B', [item[3] for item in dataBase])             # Response (ms)
    SheetUtils.update_column(spreadsheet, 'O', [item[1][166:][:-5] for item in dataBase])  # Video Link
    SheetUtils.update_column(spreadsheet, 'C', [str(item[4]) for item in dataBase])        # ID

    # Just to make the proper formatting, so that it resizes and sorts the data
    worksheet.columns_auto_resize(1, worksheet.col_count)


# Register the save_data function to be called on program exit
#atexit.register(save_data)

'''

So for the sake of saving space, things like:
    - https://nepucdn.com/bVX5JOByJBKBPrvq7eWUrxv1lbhXno7LINhm4obOnrzCLyX7N1zi8QsLbjdCXGryiVCADOujfyg8LN2ViHTJBAA9rAgt3QANDwoe16PtdhEjgPck9mmOexwKufoPPMD8kKu2c9lUIiUd49nKK/
    - .m3u8
    - https://image.tmdb.org/t/p/w1920_and_h1080_multi_faces/ 
        - Cause this seems to be a common pattern, might change if its not xD
    - 0x0x0 with _ and will be added back later!
These are appended, and then added back in later down the line, so that its easier for it to load

'''

videoDatabase = gspread.service_account().open_by_url(
    'https://docs.google.com/spreadsheets/d/1G-uQru3uOSxpkpz_NhPzv3w-2_4huRq0OKSI0O2rxE4/edit?usp=sharing')
dataBase = []


def GetMovieFromInternalID(id=1025):
    try:
        session = requests.Session()
        start_time = time.time()
        response = session.post("https://nepu.to/ajax/embed", data={"id": id})
        end_time = time.time()
        elapsed_time_ms = str(round((end_time - start_time) * 1000, 2))

        video = response.text.split('"')[5].replace('0x0x0', '_')
        preview = response.text.split('"')[7]
        formatted_datetime = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return formatted_datetime, video, preview, elapsed_time_ms, id

    except IndexError:
        # Error Handling, so basically itll just give me an error if something odsent work out right
        return "0000-00-00 00:00:00", \
            "https://nepucdn.com/bVX5JOByJBKBPrvq7eWUrxv1lbhXno7LINhm4obOnrzCLyX7N1zi8QsLbjdCXGryiVCADOujfyg8LN2ViHTJBAA9rAgt3QANDwoe16PtdhEjgPck9mmOexwKufoPPMD8kKu2c9lUIiUd49nKK/ERROR.m3u8", \
            "https://image.tmdb.org/t/p/w1920_and_h1080_multi_faces/ERROR.jpg", \
            "0.0",\
            id


def run_parallel(worker_count=16, start_index=0, num_movies=500):
    dataBase = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = []
        for i in range(start_index, start_index + num_movies):
            futures.append(executor.submit(GetMovieFromInternalID, 1025 + i))

        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=num_movies):
            result = future.result()
            dataBase.append(result)

    return sorted(dataBase, key=lambda x: x[4])


dataBase = run_parallel(48*4, 0, int(265572/32))





def Purge_Data(sheet):
    print("### PURGING DATA ###")
    worksheet = sheet.get_worksheet(2)  # Assuming the first worksheet
    range_to_clear = f'A2:Z{worksheet.row_count}'
    num_rows = worksheet.row_count
    worksheet.resize(rows=2)
    worksheet.resize(rows=num_rows)

# Initialize the gspread client and open the spreadsheet
gc = gspread.service_account()
spreadsheet = gc.open_by_url(
    'https://docs.google.com/spreadsheets/d/1G-uQru3uOSxpkpz_NhPzv3w-2_4huRq0OKSI0O2rxE4/edit?usp=sharing')

# Dynamically Resizes the Sheet, so I dont need to :D
# This might need to be fixed later if I wanted to do some internal testing
Purge_Data(spreadsheet)
worksheet = spreadsheet.get_worksheet(2)
worksheet.resize(len(dataBase) + 1, 20)



save_data()


