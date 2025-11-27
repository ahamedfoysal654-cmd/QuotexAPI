"""
Example: Place Binary Options Order

This example demonstrates how to:
1. Connect to Quotex
2. Authenticate with SSID
3. Check account balance
4. Place a binary options trade (CALL/PUT)
5. Monitor the trade result
"""

import asyncio
import os
from QuotexAPI import QuotexAPI


async def main():
    """Place order example."""
    
    # Get SSID from environment variable
    ssid = os.getenv("QUOTEX_SSID")
    if not ssid:
        print("❌ Error: QUOTEX_SSID environment variable not set")
        print("Set it with: export QUOTEX_SSID='your_ssid_token'")
        return
    
    # Initialize API
    api = QuotexAPI()
    
    try:
        # Connect to Quotex WebSocket
        print("🔌 Connecting to Quotex...")
        await api.connect()
        print("✅ Connected successfully")
        
        # Authenticate with SSID
        print(f"🔐 Authenticating with SSID...")
        await api.login_with_ssid(ssid)
        print("✅ Authenticated successfully")
        
        # Get current balance
        print("\n💰 Checking account balance...")
        balances = await api.get_balances()
        print(f"   Demo: ${balances['demo']:,.2f}")
        print(f"   Real: ${balances['real']:,.2f}")
        
        # Trade parameters
        asset = "EURUSD"
        direction = "call"  # "call" for UP, "put" for DOWN
        amount = 1.0        # Trade amount in USD
        expiry = 60         # Expiry time in seconds (1 minute)
        
        print("\n" + "="*60)
        print("TRADE PARAMETERS")
        print("="*60)
        print(f"Asset:     {asset}")
        print(f"Direction: {direction.upper()}")
        print(f"Amount:    ${amount}")
        print(f"Expiry:    {expiry} seconds")
        print(f"Account:   DEMO")
        print("="*60)
        
        # Confirm trade
        confirm = input("\n⚠️  Place this trade? (yes/no): ")
        if confirm.lower() not in ["yes", "y"]:
            print("❌ Trade cancelled")
            return
        
        # Place the trade
        print("\n📤 Placing trade...")
        trade = await api.place_trade(
            asset=asset,
            direction=direction,
            amount=amount,
            expiry=expiry,
            is_demo=True  # Use demo account
        )
        
        print("\n✅ Trade placed successfully!")
        print("="*60)
        print(f"Order ID:    {trade.order_id}")
        print(f"Asset:       {trade.asset}")
        print(f"Direction:   {trade.direction.value.upper()}")
        print(f"Amount:      ${trade.amount}")
        print(f"Open Price:  {trade.open_price:.5f}")
        print(f"Expiry:      {trade.expiry}s")
        print(f"Payout:      {trade.payout_percentage}%")
        print("="*60)
        
        # Optional: Wait for trade result
        print(f"\n⏳ Waiting for trade to expire ({expiry} seconds)...")
        
        # Countdown
        for remaining in range(expiry, 0, -5):
            print(f"   ⏱️  {remaining} seconds remaining...")
            await asyncio.sleep(5)
        
        # Final wait
        await asyncio.sleep(5)
        
        # Get updated balance
        print("\n💰 Checking updated balance...")
        new_balances = await api.get_balances()
        balance_change = new_balances['demo'] - balances['demo']
        
        print("\n" + "="*60)
        print("TRADE RESULT")
        print("="*60)
        print(f"Previous Balance: ${balances['demo']:,.2f}")
        print(f"Current Balance:  ${new_balances['demo']:,.2f}")
        print(f"Change:           ${balance_change:+,.2f}")
        
        if balance_change > 0:
            print(f"🎉 WIN! Profit: ${balance_change:.2f}")
        elif balance_change < 0:
            print(f"😔 LOSS! Loss: ${abs(balance_change):.2f}")
        else:
            print("⚖️  DRAW! No change")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Disconnect
        print("\n🔌 Disconnecting...")
        await api.disconnect()
        print("✅ Disconnected")


if __name__ == "__main__":
    asyncio.run(main())
