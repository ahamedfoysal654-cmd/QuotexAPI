"""Test trading functionality - Place buy/sell orders on Quotex."""

import asyncio
from QuotexAPI import QuotexAPI
from QuotexAPI.enums import TradeDirection
from QuotexAPI.models import TradeRequest

async def main():
    print("=" * 60)
    print("Quotex Trading Test - Place Orders")
    print("=" * 60)
    
    # Get SSID
    ssid = input("\n🔑 Enter your SSID: ").strip()
    
    # Create API instance (demo account by default)
    api = QuotexAPI(ssid=ssid, is_demo=True)
    
    try:
        # Connect
        print("\n🔌 Connecting...")
        await api.connect()
        print("✅ Connected!")
        
        # Get balance
        print("\n💰 Getting balance...")
        balance = await api.get_balance()
        print(f"Balance: ${balance.amount:.2f} ({balance.account_type.value})")
        
        # Get available assets
        print("\n📊 Getting available assets...")
        assets = await api.get_available_assets()
        
        if assets:
            print(f"Found {len(assets)} available assets:")
            # Show first 10 assets
            for i, asset in enumerate(assets[:10]):
                print(f"  {i+1}. {asset.symbol} - {asset.name}")
            if len(assets) > 10:
                print(f"  ... and {len(assets) - 10} more")
        else:
            print("No assets available, using default assets")
            assets = []
        
        # Interactive trading menu
        while True:
            print("\n" + "=" * 60)
            print("Trading Options:")
            print("=" * 60)
            print("1. Place CALL trade (price will go UP)")
            print("2. Place PUT trade (price will go DOWN)")
            print("3. Show balance")
            print("4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "4":
                break
            elif choice == "3":
                balance = await api.get_balance()
                print(f"\n💰 Balance: ${balance.amount:.2f} ({balance.account_type.value})")
                continue
            elif choice not in ["1", "2"]:
                print("❌ Invalid choice")
                continue
            
            # Get trade parameters
            print("\n📝 Trade Parameters:")
            
            # Asset selection
            print("\nPopular assets:")
            popular_assets = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "BTCUSD_otc", "ETHUSD_otc"]
            for i, asset in enumerate(popular_assets):
                print(f"  {i+1}. {asset}")
            print("  0. Enter custom asset")
            
            asset_choice = input("\nSelect asset (0-5): ").strip()
            if asset_choice == "0":
                asset = input("Enter asset symbol (e.g., EURUSD_otc): ").strip()
            elif asset_choice.isdigit() and 1 <= int(asset_choice) <= len(popular_assets):
                asset = popular_assets[int(asset_choice) - 1]
            else:
                print("❌ Invalid asset selection")
                continue
            
            # Amount
            try:
                amount = float(input("Enter amount (USD, e.g., 1): ").strip())
                if amount <= 0:
                    print("❌ Amount must be positive")
                    continue
            except ValueError:
                print("❌ Invalid amount")
                continue
            
            # Expiry time
            print("\nExpiry times:")
            print("  1. 60 seconds")
            print("  2. 120 seconds (2 minutes)")
            print("  3. 300 seconds (5 minutes)")
            print("  0. Custom")
            
            expiry_choice = input("Select expiry (0-3): ").strip()
            expiry_times = {
                "1": 60,
                "2": 120,
                "3": 300
            }
            
            if expiry_choice == "0":
                try:
                    expiry = int(input("Enter expiry in seconds: ").strip())
                    if expiry < 60:
                        print("⚠️  Warning: Expiry less than 60 seconds may not be supported")
                except ValueError:
                    print("❌ Invalid expiry")
                    continue
            elif expiry_choice in expiry_times:
                expiry = expiry_times[expiry_choice]
            else:
                print("❌ Invalid expiry selection")
                continue
            
            # Determine direction
            direction = TradeDirection.CALL if choice == "1" else TradeDirection.PUT
            
            # Confirm trade
            print("\n" + "=" * 60)
            print("📋 Trade Summary:")
            print("=" * 60)
            print(f"Asset: {asset}")
            print(f"Direction: {direction.value.upper()} ({'Price UP' if choice == '1' else 'Price DOWN'})")
            print(f"Amount: ${amount:.2f}")
            print(f"Expiry: {expiry} seconds")
            print(f"Account: DEMO")
            print("=" * 60)
            
            confirm = input("\n⚠️  Confirm trade? (yes/no): ").strip().lower()
            if confirm not in ["yes", "y"]:
                print("❌ Trade cancelled")
                continue
            
            # Place trade
            print("\n📤 Placing trade...")
            try:
                trade_request = TradeRequest(
                    asset=asset,
                    amount=amount,
                    direction=direction,
                    expiry=expiry
                )
                
                trade = await api.place_trade(trade_request)
                
                print("\n✅ Trade placed successfully!")
                print(f"   Trade ID: {trade.trade_id}")
                print(f"   Asset: {trade.asset}")
                print(f"   Direction: {trade.direction.value.upper()}")
                print(f"   Amount: ${trade.amount:.2f}")
                print(f"   Expiry: {trade.expiry}s")
                print(f"   Status: {trade.status.value}")
                
                # Option to monitor trade
                monitor = input("\n👀 Monitor trade result? (yes/no): ").strip().lower()
                if monitor in ["yes", "y"]:
                    print(f"\n⏳ Waiting for trade to expire ({expiry}s)...")
                    print("   Press Ctrl+C to stop monitoring")
                    
                    try:
                        # Wait for trade to complete
                        await asyncio.sleep(expiry + 5)  # Wait expiry + 5 seconds buffer
                        
                        # Check trade result
                        # Note: You may need to implement get_trade_result or similar
                        print("\n💡 Trade completed!")
                        print("   Check your balance to see the result")
                        
                        # Get updated balance
                        balance = await api.get_balance()
                        print(f"   Current balance: ${balance.amount:.2f}")
                        
                    except KeyboardInterrupt:
                        print("\n⏹️  Stopped monitoring")
                
            except Exception as e:
                print(f"\n❌ Trade failed: {e}")
                import traceback
                traceback.print_exc()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Disconnect
        print("\n🔌 Disconnecting...")
        await api.disconnect()
        print("✅ Done!")

if __name__ == "__main__":
    print("\n⚠️  WARNING: This is for DEMO account testing only!")
    print("Make sure is_demo=True in the code before running with real money.\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
