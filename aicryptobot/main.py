#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - main.py
import logging

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

from aicryptobot.cex.binance_api import BinanceAPI


if __name__ == "__main__":
    b = BinanceAPI("BTCUSDT", "5m")
    data = b.get_all_indicators()
    print(data)

    # b = Binance("BTCUSDT", "1h")
    # b.kdj()
