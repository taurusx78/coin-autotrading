import pyupbit
import numpy as np

df = pyupbit.get_ohlcv('KRW-MFT')  # 테스트할 가상화폐 지정
df = df['2021':]  # 해당 날짜 기준 수익률

df['range'] = (df['high'] - df['low']) * 0.01
df['target'] = df['open'] + df['range'].shift(1)

# 상승장/하락장 판별 컬럼 추가
df['bull'] = df['target'] >= df['close'].rolling(1).mean().shift(1)

fee = 0.0046  # 0.0011 + 0.0035 (업비트 수수료 + 슬리피지)


def get_hpr(h1, l1, h2, l2):
    df['ror'] = np.where((df['high'] >= df['target']) & df['bull'],
                         np.where(df['high'] / df['target'] >= h1, h1 - fee,
                                  np.where(df['low'] / df['target'] <= l1, l1 - fee, df['close'] / df['target'] - fee)),
                         np.where(df['high'] >= df['target'],
                                  np.where(df['high'] / df['target'] >= h2, h2 - fee,
                                           np.where(df['low'] / df['target'] <= l2, l2 - fee,
                                                    df['close'] / df['target'] - fee)),
                                  1))

    df['hpr'] = df['ror'].cumprod()

    # df.to_excel("data.xlsx")  # 엑셀 파일 생성

    return df['hpr'][-2]


hprs = []

for h1 in np.arange(1.05, 1.25, 0.01):
    for l1 in np.arange(0.90, 0.75, -0.01):
        for h2 in np.arange(1.05, 1.25, 0.01):
            for l2 in np.arange(0.90, 0.75, -0.01):
                hpr = get_hpr(h1, l1, h2, l2)
                if hpr < 3:
                    continue
                hprs.append((h1, l1, h2, l2, hpr))

hprs.sort(key=lambda x: x[4], reverse=True)
print(*hprs, sep='\n')

# print(round(get_hpr(1.05, 0.87, 1.05, 0.87), 4))
