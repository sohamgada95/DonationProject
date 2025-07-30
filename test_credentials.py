#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from googlesheets import get_google_sheets_client, get_sheet

def test_credentials():
    print("Testing Google Sheets credentials...")
    
    # Test client creation
    client = get_google_sheets_client()
    if client:
        print("✅ Google Sheets client created successfully")
    else:
        print("❌ Failed to create Google Sheets client")
        return False
    
    # Test sheet access
    sheet = get_sheet('donations')
    if sheet:
        print("✅ Successfully accessed 'donations' sheet")
        return True
    else:
        print("❌ Failed to access 'donations' sheet")
        return False

if __name__ == "__main__":
    test_credentials() 