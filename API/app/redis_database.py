from redis import Redis
from configparser import ConfigParser
from pathlib import Path
import string

# Redis database configuration
r = Redis(host='localhost', port='6381', decode_responses=True)
config = ConfigParser()
config.read("../conf.ini")

def reset_seetrange():
    r.mset({"sheet_range_pos1":"C9","sheet_range_pos2": f"{number_to_excel_column(2 + config.getint('GOOGLE-SHEET', 'num_columns'))}9"})
    
def get_range_name():
    return f"{r.get('sheet_range_pos1')}:{r.get('sheet_range_pos2')}"

def number_to_excel_column(n):
    """Convert a number to an Excel-style column name."""
    column_name = ""
    while n > 0:
        n, remainder = divmod(n -1, 26)
        column_name = chr(65 + remainder) + column_name
    return column_name


def update_sheetrange_1(new_row_lenght):
    pos2 = f"K{new_row_lenght}"
    r.set("sheet_range_pos2", pos2)

if __name__ == "__main__":
    print(get_range_name())