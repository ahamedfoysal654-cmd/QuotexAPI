"""Test if undetected-chromedriver can bypass Cloudflare"""
import undetected_chromedriver as uc
import time

print("Testing undetected-chromedriver...")
print("=" * 60)

# Try with headless first
print("\n1. Testing HEADLESS mode...")
options = uc.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')

try:
    print("   Starting Chrome (headless)...")
    driver = uc.Chrome(options=options)
    
    print("   Loading https://qxbroker.com...")
    driver.get("https://qxbroker.com")
    
    time.sleep(3)  # Wait for potential Cloudflare challenge
    
    title = driver.title
    source = driver.page_source.lower()
    
    print(f"   Page title: {title}")
    
    if "challenge" in source or "just a moment" in source:
        print("   ❌ HEADLESS: Cloudflare challenge detected")
    elif "qxbroker" in title.lower() or "quotex" in title.lower() or len(source) > 50000:
        print("   ✅ HEADLESS: Successfully bypassed Cloudflare!")
    else:
        print(f"   ⚠️ HEADLESS: Unclear - page length: {len(source)}, title: {title}")
    
    driver.quit()
    
except Exception as e:
    print(f"   ❌ HEADLESS ERROR: {e}")

print("\n" + "=" * 60)
print("\n2. Testing VISIBLE mode...")
options2 = uc.ChromeOptions()
# No headless - visible window

try:
    print("   Starting Chrome (visible)...")
    driver2 = uc.Chrome(options=options2)
    
    print("   Loading https://qxbroker.com...")
    driver2.get("https://qxbroker.com")
    
    print("   Waiting 5 seconds (watch for Cloudflare)...")
    time.sleep(5)
    
    title2 = driver2.title
    source2 = driver2.page_source.lower()
    
    print(f"   Page title: {title2}")
    
    if "challenge" in source2 or "just a moment" in source2:
        print("   ❌ VISIBLE: Cloudflare challenge detected")
    elif "qxbroker" in title2.lower() or "quotex" in title2.lower() or len(source2) > 50000:
        print("   ✅ VISIBLE: Successfully bypassed Cloudflare!")
    else:
        print(f"   ⚠️ VISIBLE: Unclear - page length: {len(source2)}, title: {title2}")
    
    print("\n   Browser will stay open for 5 seconds so you can see the page...")
    time.sleep(5)
    
    driver2.quit()
    
except Exception as e:
    print(f"   ❌ VISIBLE ERROR: {e}")

print("\n" + "=" * 60)
print("Test complete!")
