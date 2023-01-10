import pyupbit
import numpy as np


def get_hpr(h1, l1, h2, l2):
    try:
        df['range'] = (df['high'] - df['low']) * 0.01
        df['target'] = df['open'] + df['range'].shift(1)
        df['bull'] = df['target'] >= df['close'].shift(1)

        fee = 0.0011 + 0.0035  # 업비트 수수료 + 슬리피지

        df['ror'] = np.where((df['high'] >= df['target']) & df['bull'],
                             np.where(df['high'] / df['target'] >= h1, h1 - fee,
                                      np.where(df['low'] / df['target'] <= l1, l1 - fee, df['close'] / df['target'] - fee)),
                             np.where(df['high'] >= df['target'],
                                      np.where(df['high'] / df['target'] >= h2, h2 - fee,
                                               np.where(df['low'] / df['target'] <= l2, l2 - fee, df['close'] / df['target'] - fee)),
                                      1))

        df['hpr'] = df['ror'].cumprod()

        return df['hpr'][-2]
    except:
        return 0


tickers = pyupbit.get_tickers(fiat="KRW")

hprs = []

for ticker in tickers:
    df = pyupbit.get_ohlcv(str(ticker))

    df = df['2022':]  # 해당 날짜 기준 수익률

    for h1 in np.arange(1.05, 1.10, 0.01):
        for l1 in np.arange(0.90, 0.80, -0.01):
            for h2 in np.arange(1.05, 1.25, 0.01):
                for l2 in np.arange(0.93, 0.75, -0.01):
                    hpr = get_hpr(h1, l1, h1, l1)
                    if hpr < 3:
                        continue
                    hprs.append((ticker, h1, l1, h1, l1, hpr))

hprs.sort(key=lambda x: x[5], reverse=True)
print(*hprs, sep='\n')
