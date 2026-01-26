"""
Quick SSID Test - Verify your SSID token is valid

This script quickly tests if your SSID token works with Quotex.
Use this before running the full examples to verify authentication.
"""

import asyncio
import os
import re
from QuotexAPI import QuotexAPI

async def main():
    ssid = input("Enter your SSID token: ")
    qpi = QuotexAPI(ssid=ssid)

    await qpi.connect()

    balance = await qpi.get_balance()
    print(balance)

if __name__ == "__main__":
    asyncio.run(main())