# AICryptoBot

利用k线的一些参数 RSI MACD之类的 
虽然币圈还是挺随机的 但是这些参数可以在短期内 一定程度预测未来走向，可能也没那么准 毕竟数据可能失真

把这些数据给 chatgpt 让他分析接下来1小时 甚至15分钟的走势
然后做多或者做空 再设置止盈止损 可以调用交易所api 全自动操作


Python 3.8+
包管理器用 https://github.com/pdm-project/pdm  

需要先安装pdm 可以brew curl 也可以pip
pdm==2.20.1

# formatter
```shell

black --line-length 120 . && isort --profile black . 
```

# run

```shell
cp .env.example aicryptbot/.env
```