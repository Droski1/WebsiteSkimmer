import gspread

def getServiceAccount():
    return gspread.service_account()

def getSpreadSheet(url = 'https://docs.google.com/spreadsheets/d/1G-uQru3uOSxpkpz_NhPzv3w-2_4huRq0OKSI0O2rxE4/edit?usp=sharing'):
    return getServiceAccount().open_by_url(url)

def update_column(sheet, column_range, values):
    try:
        # Open the specified sheet
        worksheet = sheet.get_worksheet(2)  # Assuming the first worksheet

        # Determine the number of rows in the column
        num_rows = len(values)

        # Create the range for the column
        range_string = f"{column_range}2:{column_range}{num_rows + 1}"

        # Update the column with the array of values
        worksheet.update(range_string, [[value] for value in values])

        print(f'Column {column_range} has been updated successfully.')
    except:

        pass