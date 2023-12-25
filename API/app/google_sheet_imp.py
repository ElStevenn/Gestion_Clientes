import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path
import os.path
import re

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

    def get_sheet_id(self, sheet_name):
        service = self.auth()
        spreadsheet_info = service.spreadsheets().get(spreadsheetId=self.Spreadsheet_ID).execute()
        for sheet in spreadsheet_info['sheets']:
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']['sheetId']
        return None  # Or handle the case where the sheet name is not found

    def append(self, range_name, value_input_option, values):
        try:
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


        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
    

    def update_border_request(self, sheet_id, start_row_index, end_row_index, startColumnIndex, endColumnIndex, border_style = { "style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1} }):
        service = self.auth()

        # Border request
        try:
            border_requests = {
                "requests": [{
                    "updateBorders": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": start_row_index,
                            "endRowIndex": end_row_index,
                            "startColumnIndex": startColumnIndex,  # Adjust if needed
                            "endColumnIndex": endColumnIndex     # Adjust if needed
                        },
                        "top": border_style,
                        "bottom": border_style,
                        "left": border_style,
                        "right": border_style,
                        "innerHorizontal": border_style,
                        "innerVertical": border_style
                    }
                }]
            }

            # Update borders
            border_result = service.spreadsheets().batchUpdate(
                    spreadsheetId=self.Spreadsheet_ID, 
                    body=border_requests
                ).execute()
       
            return border_result
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
        

if __name__ == "__main__":
    SheetCRUD = Document_CRUD()
    SheetCRUD.Spreadsheet_ID = "1kpj7e08JrhsH4WKJhQeIYXWUh4k4Nc4vKSd-DuZqpVw"
    # SheetCRUD.auth()
    valueInputOption = "USER_ENTERED"
    range_name = "C19:K10"
    values = [["Pepero","García Olona","+34 640523319","08901","https://url.com","Mide más de 1.80","Solucionado","Vendido correctamente",""]]
    SheetCRUD.append(range_name, valueInputOption, values)