"""Better test for Cloudflare bypass"""
import undetected_chromedriver as uc
import time

print("Testing visible Chrome...")

options = uc.ChromeOptions()
driver = uc.Chrome(options=options)

try:
    print("Loading https://qxbroker.com...")
    driver.get("https://qxbroker.com")
    
    print("Waiting 5 seconds...")
    time.sleep(5)
    
    title = driver.title
    url = driver.current_url
    
    print(f"\nURL: {url}")
    print(f"Title: {title}")
    
    # More specific Cloudflare check
    source = driver.page_source
    has_challenge = "challenge-platform" in source or "cf-challenge" in source
    has_quotex_content = "quotex" in source.lower() or "qxbroker" in source.lower()
    page_size = len(source)
    
    print(f"Page size: {page_size} bytes")
    print(f"Has Cloudflare challenge elements: {has_challenge}")
    print(f"Has Quotex content: {has_quotex_content}")
    
    if has_challenge:
        print("\n❌ BLOCKED: Cloudflare challenge is active")
    elif has_quotex_content and page_size > 50000:
        print("\n✅ SUCCESS: Cloudflare bypassed!")
        print("\nBrowser will stay open - check if you see the Quotex trading page")
        print("Press Ctrl+C to close when done...")
        
        # Keep browser open
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nClosing...")
    else:
        print(f"\n⚠️ UNCLEAR: Check browser window manually")
        time.sleep(15)
    
finally:
    driver.quit()
