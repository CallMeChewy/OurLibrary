#!/usr/bin/env python3
# Quick console test to see Google API errors

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def quick_console_test():
    """Quick test to see exact console errors"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    
    try:
        print("🔍 Loading OurLibrary and checking console...")
        driver.get("https://callmechewy.github.io/OurLibrary/")
        time.sleep(10)  # Wait for all scripts to load
        
        console_logs = driver.get_log('browser')
        
        print("📝 All Console Messages:")
        for i, log in enumerate(console_logs, 1):
            print(f"{i:2d}. [{log['level']}] {log['message']}")
        
        # Look for specific Google API related messages
        api_errors = [log for log in console_logs if 'api' in log['message'].lower() or 'gapi' in log['message'].lower()]
        oauth_errors = [log for log in console_logs if 'oauth' in log['message'].lower()]
        sheets_errors = [log for log in console_logs if 'sheets' in log['message'].lower()]
        
        print(f"\n🎯 Specific Error Analysis:")
        print(f"   API-related errors: {len(api_errors)}")
        print(f"   OAuth-related errors: {len(oauth_errors)}")
        print(f"   Sheets-related errors: {len(sheets_errors)}")
        
        if api_errors:
            print("   📋 API Errors:")
            for error in api_errors:
                print(f"      - {error['message']}")
                
    finally:
        driver.quit()

if __name__ == "__main__":
    quick_console_test()