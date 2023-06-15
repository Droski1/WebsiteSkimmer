from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import SheetUtils
import gspread
import concurrent.futures
import concurrent.futures
import threading
import time
import concurrent.futures
import tqdm
from datetime import datetime
import requests

# Initialize the gspread client and open the spreadsheet
gc = gspread.service_account()
spreadsheet = gc.open_by_url(
    'https://docs.google.com/spreadsheets/d/1G-uQru3uOSxpkpz_NhPzv3w-2_4huRq0OKSI0O2rxE4/edit?usp=sharing')

# Create a lock for synchronizing the saving process
save_lock = threading.Lock()
def Purge_Data(sheet):
    print("### PURGING DATA ###")
    worksheet = sheet.get_worksheet(2)  # Assuming the first worksheet
    range_to_clear = f'A3:Z{worksheet.row_count}'
    num_rows = worksheet.row_count
    worksheet.resize(rows=2)
    worksheet.resize(rows=num_rows)

def save_data(data, spreadsheet):
    worksheet = spreadsheet.get_worksheet(2)
    Purge_Data(spreadsheet)
    data = sorted(data, key=lambda x: x[4])
    # Call the update_column function
    SheetUtils.update_column(worksheet, 'A', [item[0] for item in data])             # Updated Date
    SheetUtils.update_column(worksheet, 'I', [item[2][55:][:-4] for item in data])   # Preview
    SheetUtils.update_column(worksheet, 'B', [item[3] for item in data])             # Response (ms)
    SheetUtils.update_column(worksheet, 'O', [item[1][166:][:-5] for item in data])  # Video Link
    SheetUtils.update_column(worksheet, 'C', [item[4] for item in data])        # ID

    worksheet.resize(len(data) + 1, 20)

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
        elapsed_time_ms = int(round((end_time - start_time) * 1000, 2))

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

def save_data_periodically(data, spreadsheet):
    # Periodically save the data every 100-200 iterations
    while True:
        time.sleep(20)  # Adjust the sleep duration as needed
        with save_lock:
            save_data(data, spreadsheet)

def run_parallel(worker_count=16, start_index=0, num_movies=500):
    dataBase = []

    # Create a separate thread for periodically saving the data
    save_thread = threading.Thread(target=save_data_periodically, args=(dataBase, spreadsheet))
    save_thread.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = []
        for i in range(start_index, start_index + num_movies):
            futures.append(executor.submit(GetMovieFromInternalID, 1025 + i))

            if len(futures) % 100 == 0 and 100 <= len(futures) <= 200:
                with save_lock:
                    # Acquire the lock before saving the data
                    save_data(dataBase, spreadsheet)

        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=num_movies):
            result = future.result()
            dataBase.append(result)

    # Wait for the save thread to finish before returning the data
    save_thread.join()

    return sorted(dataBase, key=lambda x: x[4])



dataBase = run_parallel(24, 0, int(265572/32))







save_data()


