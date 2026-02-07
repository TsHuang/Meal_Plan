import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys

def fetch_dishes_from_sheets(credential_path, sheet_name):
    """
    Connects to Google Sheets using a service account JSON file
    and fetches the content of the specified spreadsheet.
    """
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(credential_path, scope)
        client = gspread.authorize(creds)
        
        # Open the spreadsheet
        # You can open by name: client.open("Dish List")
        # Or by key: client.open_by_key("...")
        # Here we assume user provides the Exact Name of the sheet
        sheet = client.open(sheet_name).sheet1
        
        # Get all records
        records = sheet.get_all_records()
        
        # Convert to list of dicts compatible with our existing MealPlanner
        # gspread get_all_records returns list of dicts automatically
        
        # Data validation / Transformation if necessary
        # Ensure column names map correctly if they differ, but assuming they match CSV headers
        return records
        
    except FileNotFoundError:
        print(f"Error: Credential file '{credential_path}' not found.")
        sys.exit(1)
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Spreadsheet '{sheet_name}' not found. Please check the name and share it with the service account email.")
        sys.exit(1)
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        sys.exit(1)
