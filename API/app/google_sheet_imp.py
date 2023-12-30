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
        
    def extract_row_index(self, range_string):
        # Pattern to match the row number in the range string (e.g., '5' in 'Sheet1!A5:Z5')
        match = re.search(r'(\d+)', range_string.split('!')[1])
        if match:
            return int(match.group(1)) - 1  # Subtract 1 to convert to zero-based index
        else:
            return 0  # Default to 0 if no match is found
    
    @feature_decorator
    def read_excel(self, range_name, enum=False) -> np.ndarray:
        """Read the range and return enumerated if requested, excluding the header."""
        service = self.auth()            

        result = (
            service.spreadsheets().values()
            .get(spreadsheetId=self.Spreadsheet_ID, range=range_name)
            .execute()
        )

        pre_result = np.array(result.get('values', None))
        return pre_result
        
        # Check if pre_result is None and return an empty array if so
        if pre_result is None:
            return np.array([])

        n_rows = pre_result.shape[0]
        n_cols = 9 # Modify this if is required
        result_ = np.full((n_rows, n_cols), '', dtype=object)

        if enum:
                for i, row in enumerate(pre_result):
                    result_[i, 0] = str(i)
                    result_[i, 1:] = row
        else:
            for i, row in enumerate(pre_result):
                result_[i, :len(row)] = row or ''

        return result_

    @feature_decorator
    def send_message(self, message, type = "warning", error_message=["An error ocurred"], ):
        range_name = "B4:B5"
        values = [
            [error_message[0]],
            [message]
        ]

        data = [
            {"range": range_name, "values": values}
        ]

        if type == "warning":
            background_color = "#fcba03"
        elif type == "error":
            background_color = "#fc0303"
        elif type == "message":
            background_color = "#3dfc03"
        else:
            background_color = "#030bfc"

        body = {"valueInputOption": "USER_ENTERED", "data": data}
        result = (
            self.service_.spreadsheets().values()
            .batchUpdate(spreadsheetId=self.Spreadsheet_ID, body=body)
            .execute()
        )
        print(f"{(result.get('totalUpdatedCells'))} cells updated.")


    





        return result.get('totalUpdatedCells', None)


if __name__ == "__main__":

    SheetCRUD = Document_CRUD()
    SheetCRUD.Spreadsheet_ID = "1kpj7e08JrhsH4WKJhQeIYXWUh4k4Nc4vKSd-DuZqpVw"

    # range_name = "C9:K9999999"
    # result = SheetCRUD.read_excel(range_name, enum=False)
    # print(result)
    # print(result.shape)
    SheetCRUD.send_message("You what happened!")


    
    # SheetCRUD.Spreadsheet_ID = "1kpj7e08JrhsH4WKJhQeIYXWUh4k4Nc4vKSd-DuZqpVw"
    # # SheetCRUD.auth()
    valueInputOption = "USER_ENTERED"
    range_name = "C19:K10"
    # values = [["Pepero","García Olona","+34 640523319","08901","https://url.com","Mide más de 1.80","Solucionado","Vendido correctamente",""]]
    # SheetCRUD.append(range_name, valueInputOption, final.tolist())