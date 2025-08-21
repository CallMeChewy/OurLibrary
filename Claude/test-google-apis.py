#!/usr/bin/env python3
# Test Google APIs availability

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_google_apis():
    """Test if Google APIs are accessible"""
    
    print("🧪 Testing Google APIs Accessibility")
    print("=" * 40)
    
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    try:
        # Go to a simple test page with Google API loading
        driver.get("data:text/html,<html><head><script src='https://apis.google.com/js/api.js'></script></head><body><script>gapi.load('client', function() { console.log('GAPI client loaded'); gapi.client.init({ apiKey: 'AIzaSyAsG8hleX4WRKCLcIJdWkcNptWNMGdNjzk', discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/sheets/v4/rest'] }).then(function() { console.log('Sheets API initialized successfully'); }).catch(function(error) { console.error('Sheets API initialization failed:', error); }); });</script></body></html>")
        
        time.sleep(5)  # Wait for API loading
        
        # Get console logs
        console_logs = driver.get_log('browser')
        
        print("🔍 Google API Test Results:")
        for log in console_logs:
            print(f"   [{log['level']}] {log['message']}")
        
        # Check for specific results
        gapi_loaded = any('GAPI client loaded' in log['message'] for log in console_logs)
        sheets_success = any('Sheets API initialized successfully' in log['message'] for log in console_logs)
        sheets_failed = any('Sheets API initialization failed' in log['message'] for log in console_logs)
        
        print(f"\n📊 Results:")
        print(f"   GAPI Client Loaded: {'✅' if gapi_loaded else '❌'}")
        print(f"   Sheets API Success: {'✅' if sheets_success else '❌'}")
        print(f"   Sheets API Failed: {'❌' if sheets_failed else '✅'}")
        
        if sheets_success:
            print("✅ Google Sheets API is accessible with your API key")
            return True
        elif sheets_failed:
            print("❌ Google Sheets API initialization failed")
            return False
        else:
            print("⚠️ Inconclusive results")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_google_apis()
    print(f"\n🏁 Google APIs test: {'✅ PASSED' if success else '❌ FAILED'}")