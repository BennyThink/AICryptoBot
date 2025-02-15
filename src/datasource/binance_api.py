#!/usr/bin/env python3
# coding: utf-8
# AICryptoBot - binance_cex.py


import logging
import os

import pandas as pd
from binance.um_futures import UMFutures

from datasource import DataSource


class BinanceAPI(DataSource):

    def __init__(self, symbol: str = None, interval: str = "15m", count=50):
        api_key, api_secret = (os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))
        self.__um_client = UMFutures(key=api_key, secret=api_secret)
        self.df = pd.DataFrame()
        self.__symbol = symbol
        self.__interval = interval
        self.__count = count
        if symbol is not None:
            self._candlestick()

    def _candlestick(self):
        # K线数据：开盘价、收盘价、最高价、最低价（最好包含多个时间段）
        candles = self.__um_client.klines(symbol=self.__symbol, interval=self.__interval, limit=100 + self.__count)
        columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "transaction_value",
            "transaction_count",
            "active_buy_volume",
            "active_buy_value",
            "ignore",
        ]

        self.df = pd.DataFrame(candles, columns=columns)
        numeric_columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "transaction_value",
            "transaction_count",
            "active_buy_volume",
            "active_buy_value",
        ]
        self.df[numeric_columns] = self.df[numeric_columns].apply(pd.to_numeric)
        self.df["open_time"] = pd.to_datetime(self.df["open_time"], unit="ms")
        self.df["close_time"] = pd.to_datetime(self.df["close_time"], unit="ms")

    def get_all_indicators(self) -> str:
        logging.debug("获取 %s %s的技术指标中....", self.__symbol, self.__interval)
        self._boll()
        self._rsi()
        self._macd()
        self._volume()
        self._ma()
        self.df.drop(columns=["ignore", "close_time", "transaction_value", "transaction_count", "ema99"], inplace=True)
        self.df.dropna(inplace=True)
        # 转换数据格式 rsi保留整数，macd boll ema active_buy_value 保留两位小数
        self.df["rsi6"] = self.df["rsi6"].astype(int)
        self.df["rsi12"] = self.df["rsi12"].astype(int)
        self.df["rsi24"] = self.df["rsi24"].astype(int)
        self.df["dif"] = self.df["dif"].round(2)
        self.df["dea"] = self.df["dea"].round(2)
        self.df["macd"] = self.df["macd"].round(2)
        self.df["upperband"] = self.df["upperband"].round(2)
        self.df["middleband"] = self.df["middleband"].round(2)
        self.df["lowerband"] = self.df["lowerband"].round(2)
        self.df["ema7"] = self.df["ema7"].round(2)
        self.df["ema25"] = self.df["ema25"].round(2)
        self.df["active_buy_value"] = self.df["active_buy_value"].round(2)

        # 秒级时间戳
        return self.df.to_json(orient="records", date_format="epoch", date_unit="s")

    def __str__(self):
        return "binance"

    def get_usdt_balance(self):
        assets = self.__um_client.balance()
        for asset in assets:
            if asset["asset"] == "USDT":
                return asset

    def new_order(self, side, usdt, leverage=5):
        price = self.get_price()
        # 需要处理一下精度问题
        quantity = round(usdt / price, 3)
        logging.info("%s：%s，数量：%s", self.__symbol, "做空" if side == "SELL" else "做多", quantity)
        self.__um_client.change_leverage(symbol=self.__symbol, leverage=leverage)
        self.__um_client.new_order(symbol=self.__symbol, side=side, quantity=quantity, type="MARKET")

    def get_holdings(self) -> list:
        data = self.__um_client.get_position_risk(symbol=self.__symbol)
        return data

    def close_holdings(self, quantity=None):
        position = self.get_holdings()
        position_amount = float(position[0]["positionAmt"])
        if quantity is None:
            quantity = abs(position_amount)
        # positionAmt>0 做多，positionAmt<0 做空
        if position_amount > 0:
            logging.info("做多平仓，数量：%s", quantity)
            self.__um_client.new_order(symbol=self.__symbol, side="SELL", closePosition=True, type="MARKET")
        else:
            logging.info("做空平仓，数量：%s", quantity)
            self.__um_client.new_order(symbol=self.__symbol, side="BUY", closePosition=True, type="MARKET")

    def get_price(self) -> float:
        # 1 个币的价格，单位 USDT
        return float(self.__um_client.ticker_price(symbol=self.__symbol)["price"])
