"""Test visible Chrome only"""
import undetected_chromedriver as uc
import time

print("Testing VISIBLE Chrome with undetected-chromedriver...")
print("=" * 60)

options = uc.ChromeOptions()
# No headless - completely visible

try:
    print("\nStarting Chrome (visible window)...")
    driver = uc.Chrome(options=options)
    
    print("Loading https://qxbroker.com...")
    driver.get("https://qxbroker.com")
    
    print("Waiting 8 seconds for page to load and Cloudflare to clear...")
    time.sleep(8)
    
    try:
        title = driver.title
        source = driver.page_source.lower()
        url = driver.current_url
        
        print(f"\nResults:")
        print(f"  Current URL: {url}")
        print(f"  Page title: {title}")
        print(f"  Page size: {len(source)} bytes")
        
        if "challenge" in source or "just a moment" in source or "un instant" in source:
            print("\n  ❌ Cloudflare challenge still showing")
        elif "qxbroker" in title.lower() or "quotex" in title.lower() or len(source) > 50000:
            print("\n  ✅ Successfully loaded! Cloudflare bypassed")
            print("\n  Testing WebSocket connection...")
            
            # Try to inject code to monitor WebSocket
            script = """
            // Monitor WebSocket connections
            const originalWS = window.WebSocket;
            window.WebSocket = function(...args) {
                console.log('WebSocket created:', args[0]);
                window._last_ws_url = args[0];
                const ws = new originalWS(...args);
                window._quotex_ws = ws;
                
                ws.addEventListener('open', () => console.log('WS OPEN'));
                ws.addEventListener('message', (e) => console.log('WS MSG:', e.data.substring(0, 100)));
                ws.addEventListener('error', (e) => console.log('WS ERROR:', e));
                ws.addEventListener('close', () => console.log('WS CLOSE'));
                
                return ws;
            };
            return 'WebSocket monitor installed';
            """
            
            result = driver.execute_script(script)
            print(f"  WebSocket monitor: {result}")
            
            print("\n  Waiting 10 seconds to see if WebSocket connects...")
            time.sleep(10)
            
            # Check console logs
            logs = driver.get_log('browser')
            ws_logs = [log for log in logs if 'WS' in log.get('message', '')]
            if ws_logs:
                print(f"\n  WebSocket activity detected:")
                for log in ws_logs[:5]:  # First 5
                    print(f"    {log['message'][:150]}")
            else:
                print("\n  No WebSocket activity detected yet")
                
        else:
            print(f"\n  ⚠️ Unclear state - check the browser window")
        
        print("\n  Browser will stay open for 10 more seconds...")
        print("  (Check the browser window manually)")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n  ❌ Error getting page info: {e}")
    
    print("\nClosing browser...")
    driver.quit()
    print("Done!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
