#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def check_deployment_status():
    """Check if the latest changes are deployed"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-cache")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        timestamp = int(time.time())
        url = f"https://callmechewy.github.io/OurLibrary/index.html?cb={timestamp}"
        
        driver.get(url)
        time.sleep(3)
        
        # Check if the new redirect code is present
        has_redirect = driver.execute_script("""
            const pageSource = document.documentElement.innerHTML;
            return pageSource.includes('auth-demo.html?email=') && 
                   pageSource.includes('encodeURIComponent(email)');
        """)
        
        print(f"URL checked: {url}")
        print(f"Has redirect code: {has_redirect}")
        
        if has_redirect:
            print("✅ DEPLOYMENT COMPLETE - New redirect code is live")
        else:
            print("⏳ DEPLOYMENT PENDING - Still showing old code")
            
        return has_redirect
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    check_deployment_status()