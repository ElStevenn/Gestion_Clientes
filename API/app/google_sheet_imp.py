#!/usr/bin/env python3
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path
import os.path
import re
import numpy as np
import pandas as pd
from typing import Optional, Tuple

# Get credentials from this file
credentials_file = "/home/ubuntu/certificates/google_cloud_credentials/credentials.json"
token_file = "/home/ubuntu/certificates/google_cloud_credentials/token.json"
SERVICE_ACCOUNT_FILE = '/home/ubuntu/certificates/google_cloud_credentials/'

class Document_CRUD():
    """
    
        *add description here explaining what exacly is this*
    
    """
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    def __init__(self, Spreadsheet_ID=None):
        self.Spreadsheet_ID = Spreadsheet_ID
        self.service_ = self.auth()
        self.column_rangeName = "C8:K8"

    def generate_auth_url(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, self.SCOPES)
        flow.redirect_uri = 'http://185.254.206.129/code'  # Your redirect URI

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')
        
        return authorization_url

    def exchange_code(self, code):
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, self.SCOPES)
        flow.redirect_uri = 'http://185.254.206.129/code'  # Your redirect URI

        flow.fetch_token(code=code)

        # Save the credentials for the next run
        with open(token_file, "w") as token_file_obj:
            token_file_obj.write(flow.credentials.to_json())

        return flow.credentials

    def auth(self):
        creds = None
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise Exception("No valid credentials provided. Run the authorization process.")
        return build("sheets", "v4", credentials=creds)

    def feature_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HttpError as error:
                print(f"An error occurred: {error}")
                return error
        return wrapper
                       

    def get_sheet_id(self, sheet_name):
        service = self.auth()
        spreadsheet_info = service.spreadsheets().get(spreadsheetId=self.Spreadsheet_ID).execute()
        for sheet in spreadsheet_info['sheets']:
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']['sheetId']
        return None  # Or handle the case where the sheet name is not found

    @feature_decorator
    def append(self, range_name, value_input_option, values):
        service = self.auth()

        # Append data to the sheet
        body = {"values": values}
        append_result = service.spreadsheets().values().append(
            spreadsheetId=self.Spreadsheet_ID,
            range=range_name,
            valueInputOption=value_input_option,
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()

        # Calculate the new row indices for borders
        updated_range = append_result.get('updates', {}).get('updatedRange', '')
        start_row_index = self.extract_row_index(updated_range)
        num_rows = append_result.get('updates', {}).get('updatedRows', 0)
        end_row_index = start_row_index + num_rows

        # Assuming you have a valid method to get the sheet ID
        sheet_id = self.get_sheet_id("Your Sheet Name")  # Replace "Your Sheet Name" with the actual sheet name

        # Call function to print the borders
        self.update_border_request(sheet_id, start_row_index, end_row_index, 2, 11)

    

    def update_border_request(self, sheet_id, start_row_index, end_row_index, start_column_index, end_column_index, 
                                    border_style=None, new_title=None):
        if border_style is None:
            border_style = {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}}

        service = self.auth()

        # Initialize requests list
        requests = []

        # Adding border update request
        border_request = {
            "updateBorders": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": start_row_index,
                    "endRowIndex": end_row_index,
                    "startColumnIndex": start_column_index,
                    "endColumnIndex": end_column_index
                },
                "top": border_style,
                "bottom": border_style,
                "left": border_style,
                "right": border_style,
                "innerHorizontal": border_style,
                "innerVertical": border_style
            }
        }
        requests.append(border_request)

        # Adding spreadsheet properties update request, if a new title is provided
        if new_title:
            properties_request = {
                "updateSpreadsheetProperties": {
                    "properties": {
                        "title": new_title
                    },
                    "fields": "title"
                }
            }
            requests.append(properties_request)

        # Sending the batch update request
        try:
            result = service.spreadsheets().batchUpdate(
                spreadsheetId=self.Spreadsheet_ID, 
                body={"requests": requests}
            ).execute()

            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
    
    def column_to_index(column: str):
        """Convert a spreadsheet column letter to a zero-based index."""
        # return -> int
        index = 0
        for char in column:
            index = index * 26 + (ord(char.upper()) - ord('A')) + 1
        return index - 1  # zero-based index

    def calc_index(self, range_name: Optional[str] = "B1:B2"):
        """
        Calculate the start and end indices for rows and columns based on a range in A1 notation.

        Returns:
            tuple: (startRowIndex, endRowIndex, startColumnIndex, endColumnIndex)
        """
        # Regex to extract the column letters and row numbers from the range
        match = re.match(r'([A-Z]+)(\d+):([A-Z]+)(\d+)', range_name)
        if not match:
            raise ValueError("Invalid range. Please use a range in A1 notation (e.g., 'B1:B2').")

        start_col, start_row, end_col, end_row = match.groups()

        # Convert column letters to zero-based indices using the static method
        start_col_index = Document_CRUD.column_to_index(start_col)
        end_col_index = Document_CRUD.column_to_index(end_col)

        # Convert row numbers to zero-based indices
        start_row_index = int(start_row) - 1
        end_row_index = int(end_row) - 1

        return (start_row_index, end_row_index, start_col_index, end_col_index)

    def extract_row_index(self, range_string):
        # Pattern to match the row number in the range string (e.g., '5' in 'Sheet1!A5:Z5')
        match = re.search(r'(\d+)', range_string.split('!')[1])
        if match:
            return int(match.group(1)) - 1  # Subtract 1 to convert to zero-based index
        else:
            return 0  # Default to 0 if no match is found
    
    @feature_decorator
    def read_excel(self, range_name, enum=False):
        """
        Read the range and return enumerated if requested, excluding the header. 
        
        enum: enum parameter is used to enumerate/add index when it comes to read the excel
        """        
        
        result = (
            self.service_.spreadsheets().values()
            .get(spreadsheetId=self.Spreadsheet_ID, range=range_name)
            .execute()
        )
        try:
            pre_result = result.get('values', [])
        except Exception as e:
            self.send_message(f"An error occurred: {e}", "error")
            return np.array([])

        # Asign num columns
        n_cols = self.get_num_cols(range_name)
        # Check if pre_result is empty and return an empty array if so
        if not pre_result:
            return np.array([])

        # Create a result array with an additional column for enumeration if needed
        result_ = np.full((len(pre_result), n_cols), '', dtype=object)

        # Populate the result array
        for i, row in enumerate(pre_result):
            if enum:
                result_[i, 0] = str(i)  # Enumeration column
                end_col = min(len(row) + 1, n_cols)
                result_[i, 1:end_col] = row[:end_col - 1]
            else:
                end_col = min(len(row), n_cols)
                result_[i, :end_col] = row[:end_col]

        return np.array(result_)

    def get_num_cols(self, range_name) -> int:
        pattern = r"([A-Z])\d:([A-Z])\d+"
        match = re.search(pattern, str(range_name))
        if match:
            letters = match.groups()
            return int((ord(letters[1].upper()) - 64) - (ord(letters[0].upper()) - 64)) + 2
        else:
            self.send_message("Something was wrong when it comes to read the range", "error")
            return None
        
    @feature_decorator
    def send_message(self, message, type = "warning", error_message=None, range_name = "B4:B5"):

        if type == "warning":
            background_color = [252, 186, 3]
            error_message = "Something has happened" if error_message is None else error_message
        elif type == "error":
            background_color = [252, 3, 3]
            error_message = "An error ocurred" if error_message is None else error_message
        elif type == "message":
            error_message = "A message recived" if error_message is None else error_message
            background_color = [61, 252, 3]
        else:
            error_message = "Something has happended" if error_message is None else error_message
            background_color = [3, 11, 252]

        values = [
            [error_message],  # First row (B4)
            [message]         # Second row (B5)
        ]

        data = [
            {"range": range_name, "values": values}
        ]

        body = {"valueInputOption": "USER_ENTERED", "data": data}
        
        try:
            result = (
                self.service_.spreadsheets().values()
                .batchUpdate(spreadsheetId=self.Spreadsheet_ID, body=body)
                .execute()
            )
            print(f"{result.get('totalUpdatedCells')} cells updated.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        border_style = {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}}
        index = self.calc_index(range_name)

        requests = [
            {
                "updateBorders": {
                    "range": {
                        "sheetId": self.get_sheet_id("pau's spreadseet"), 
                        "startRowIndex": index[0],
                        "endRowIndex": index[1],
                        "startColumnIndex": index[2],
                        "endColumnIndex": index[3] 
                    },
                    "top": border_style,
                    "bottom": border_style,
                    "left": border_style,
                    "right": border_style,
                    "innerHorizontal": border_style,
                    "innerVertical": border_style
                }
            },
            {
                "repeatCell": {
                    "range": {
                        "sheetId": self.get_sheet_id("pau's spreadsheet"),
                        "startRowIndex": index[0],
                        "endRowIndex": index[1],
                        "startColumnIndex": index[2],
                        "endColumnIndex": index[3] 
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": background_color[0] / 255.0,
                                "green": background_color[1] / 255.0,
                                "blue": background_color[2] / 255.0,
                                "alpha": 1
                            }
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            }
        ]
        
     
        self.service_.spreadsheets().batchUpdate(
            spreadsheetId=self.Spreadsheet_ID, 
            body={"requests": requests}
        ).execute()


        return result.get('totalUpdatedCells', None)

    @feature_decorator
    def clear_cell_formatting(self):
        sheet_id = self.get_sheet_id("pau's spreadsheet")  # Ensure this returns the correct sheet ID
        # Define the range to clear
        requests = [{
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 3, 
                    "endRowIndex": 5,   
                    "startColumnIndex": 1,
                    "endColumnIndex": 3    
                },
                "fields": "userEnteredValue,userEnteredFormat.backgroundColor,userEnteredFormat.borders"  # Fields to clear
            }
        }]

        body = {
            "requests": requests
        }

        # Make the API call to batchUpdate
        response = self.service_.spreadsheets().batchUpdate(
            spreadsheetId=self.Spreadsheet_ID,  # Ensure this is the correct spreadsheet ID
            body=body
        ).execute()
        print(f"Cleared cell formatting: {response}")


    @feature_decorator
    def get_all_columns_name_and_status(self):
        """
        Get all the column name and if is in italic mode or no

        """

        range_name = "C8:Z8" # This is the range where the function read, change if is needed
        sheet = self.service_.spreadsheets()
        data_format_result = sheet.get(spreadsheetId=self.Spreadsheet_ID, ranges=range_name,
                   fields='sheets(data(rowData(values(effectiveFormat(textFormat(italic))))))').execute()
        
        result = sheet.values().get(spreadsheetId=self.Spreadsheet_ID, range=range_name).execute().get('values', [])[0]
        
        _result = []
        print(len(result))
        print(len(data_format_result.get('sheets', [])[0].get('data', [])[0].get('rowData', [])[0].get('values', [])))
        """
        try:
            for i, value in enumerate(data_format_result.get('sheets', [])[0].get('data', [])[0].get('rowData', [])[0].get('values', [])):
                _result.append({
                    'value': result[i],
                    'is_italic': True if value.get('effectiveFormat', None).get('textFormat', None).get('italic', None) else False
                    # We can add more states here as needed 
                })
        except IndexError:
            # In case the user fo
            self.send_message("Asegurate de quitar el italic para que no lo detecte como campo, es probable que acabes de quitar una columna", "error", "Error de campo", range_name="B1:B2")
            raise IndexError("There is a cell in the column name definition, where is italic, make sure to remove the \"italic\" in the cell")
            
        """
        return _result
        


if __name__ == "__main__":

    SheetCRUD = Document_CRUD()
    SheetCRUD.Spreadsheet_ID = "1kpj7e08JrhsH4WKJhQeIYXWUh4k4Nc4vKSd-DuZqpVw"

    range_name = "C9:L99999999"
    result = SheetCRUD.get_all_columns_name_and_status()
    print(result)

  

    valueInputOption = "USER_ENTERED"
    range_name = "C19:K10"
