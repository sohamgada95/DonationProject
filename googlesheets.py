import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid
import os
import json

# Google Sheets configuration
GOOGLE_SPREADSHEET_ID = '18m_9aCJZBO49G9Ki41n4NedNugYB5yquz6yQtyyQ9JE'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_sheets_client():
    """Initialize and return Google Sheets client"""
    try:
        # Try to get credentials from environment variable first (for Vercel)
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if credentials_json:
            # Parse the JSON string from environment variable
            creds_dict = json.loads(credentials_json)
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        else:
            # Fallback to file for local development
            creds = Credentials.from_service_account_file('gs_credentials.json', scopes=SCOPES)
        
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Error initializing Google Sheets client: {e}")
        return None

def get_sheet(sheet_name):
    """Get a specific sheet by name"""
    try:
        client = get_google_sheets_client()
        if not client:
            return None
        spreadsheet = client.open_by_key(GOOGLE_SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet
    except Exception as e:
        print(f"Error getting sheet {sheet_name}: {e}")
        return None

def gs_read(sheet_name, filters=None):
    """
    Read data from Google Sheets
    Args:
        sheet_name (str): Name of the sheet
        filters (dict): Optional filters like {'building': 'A', 'flat_number': 101}
    Returns:
        list: List of dictionaries representing records
    """
    try:
        worksheet = get_sheet(sheet_name)
        if not worksheet:
            return []
        all_data = worksheet.get_all_records()
        if filters:
            filtered_data = []
            for record in all_data:
                match = True
                for key, value in filters.items():
                    if str(record.get(key, '')) != str(value):
                        match = False
                        break
                if match:
                    filtered_data.append(record)
            return filtered_data
        return all_data
    except Exception as e:
        print(f"Error reading from {sheet_name}: {e}")
        return []

def gs_create(sheet_name, data):
    """
    Create a new record in Google Sheets
    Args:
        sheet_name (str): Name of the sheet
        data (dict): Data to insert
    Returns:
        dict: Created record with ID, or None if failed
    """
    try:
        worksheet = get_sheet(sheet_name)
        if not worksheet:
            return None
        # Generate ID if not provided
        if 'id' not in data or not data['id']:
            existing_data = worksheet.get_all_records()
            max_id = 0
            for record in existing_data:
                try:
                    record_id = int(record.get('id', 0))
                    max_id = max(max_id, record_id)
                except (ValueError, TypeError):
                    continue
            data['id'] = max_id + 1
        # Generate receipt_token if not provided
        if 'receipt_token' not in data or not data['receipt_token']:
            data['receipt_token'] = uuid.uuid4().hex
        # Set date if not provided
        if 'date' not in data or not data['date']:
            data['date'] = datetime.now().strftime('%Y-%m-%d')
        # Convert data to list for insertion
        headers = worksheet.row_values(1)
        row_data = []
        for header in headers:
            row_data.append(data.get(header, ''))
        worksheet.append_row(row_data)
        return data
    except Exception as e:
        print(f"Error creating record in {sheet_name}: {e}")
        return None 