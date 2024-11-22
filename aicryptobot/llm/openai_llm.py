#!/usr/bin/env python3
# coding: utf-8

# AICryptoBot - openai_llm.py

import json
import logging
import os

from openai import AzureOpenAI, OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from llm import LLM
from llm.definition import TradingAction


class GPT(LLM):
    def __init__(self):
        prefix, provider = "", os.getenv("OPENAI_PROVIDER", "OpenAI")
        if provider == "Azure":
            prefix = "AZURE_"
        base_url, api_key, model = (
            os.getenv(f"{prefix}OPENAI_BASE_URL"),
            os.getenv(f"{prefix}OPENAI_API_KEY"),
            os.getenv(f"{prefix}OPENAI_MODEL"),
        )

        if provider == "Azure":
            logging.info("使用 Azure OpenAI API")
            self.client = AzureOpenAI(api_key=api_key, api_version="2024-10-01-preview", azure_endpoint=base_url)
        else:
            logging.info("使用 OpenAI API")
            self.client = OpenAI(base_url=base_url, api_key=api_key)

        self.model = model

    @retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(3))
    def __create(self, messages):
        return self.client.chat.completions.create(model=self.model, temperature=0.1, messages=messages)

    def send(self, symbol: str, indicators: list, holdings: list) -> TradingAction:
        logging.info("发送数据给 %s %s", self.client, self.model)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Token to analyze: {symbol}"},
        ]
        for indicator in indicators:
            messages.append({"role": "user", "content": indicator})
        # holdings 必须和当前数据匹配
        if holdings and holdings[0]["symbol"] == symbol:
            logging.info("已有持仓，添加额外信息中...")
            messages.append({"role": "user", "content": f"My current holdings: {holdings}"})
        try:
            completion = self.__create(messages)
            return json.loads(completion.choices[0].message.content)
        except:
            logging.error("%s:OpenAI API 请求失败", symbol)
            return {
                "action": "N/A",
                "detail": "",
                "take_profit": {"usdt": 0, "percentage": 0},
                "stop_loss": {"usdt": 0, "percentage": 0},
            }
