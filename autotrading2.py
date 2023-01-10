import pyupbit
import requests
import datetime
import time
import math
from dotenv import load_dotenv
import os

# .env 파일 불러오기
load_dotenv()

acc = os.environ.get('UPBIT_ACCESS_KEY')
sec = os.environ.get('UPBIT_SECRET_KEY')
myToken = os.environ.get('SLACK_TOKEN')


# 슬랙 알림 전송
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )


# 매매 단위 맞추기
def setup_unit(target):
    target = round(target, 3 - len(str(int(target))))
    return target


# 목표가 조회 & 상승장/하락장 판별
def get_target_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    start = df.iloc[-1]["open"]
    target = start + (df.iloc[-2]["high"] - df.iloc[-2]["low"]) * 0.01
    bull = target >= df.iloc[-2]["close"]
    return start, target, math.ceil(target), bull


# 로그인
upbit = pyupbit.Upbit(acc, sec)

ticker = "KRW-MOC"  # 투자할 가상화폐 지정
start, target, buy_price, bull = get_target_price(ticker)

now = datetime.datetime.now()
reset_time = pyupbit.get_ohlcv(
    ticker, interval="day", count=1).index[0] + datetime.timedelta(days=1)
reset = True

state = 0  # 0: 매수전, 1: 미체결/보유, 2: 매도후
buy_date = 0  # 0: 전일 매수, 1: 금일 매수
sell_chance = 1  # 매도 기회
sell_all_cnt = 0  # 전량 매도 기회
max_rate = 1
post_message(myToken, "#coin", "목표가: " + str(target) +
             ", " + str(bull) + ", state: " + str(state))

while True:
    try:
        now = datetime.datetime.now()
        current_price = pyupbit.get_current_price(ticker)

        # 09:00 초기화 준비
        while reset_time - datetime.timedelta(seconds=5) <= now < reset_time:
            now = datetime.datetime.now()
            reset = False
            time.sleep(0.5)

        # 09:00 초기화 진행
        while not reset and reset_time <= now < reset_time + datetime.timedelta(seconds=30):
            now = datetime.datetime.now()
            start, temp, buy_price, bull = get_target_price(ticker)

            # 시가가 업데이트 된 경우
            if target != temp or reset_time + datetime.timedelta(seconds=28) <= now:
                target = temp
                reset_time = pyupbit.get_ohlcv(
                    ticker, interval="day", count=1).index[0] + datetime.timedelta(days=1)
                reset = True
                if state == 2 or state == 4:
                    state = 0
                buy_date, sell_chance, sell_all_cnt = 0, 0, 0
                max_rate = 1
                post_message(myToken, "#coin", "목표가: " + str(target) +
                             ", " + str(bull) + ", state: " + str(state))
                break  # while문 탈출

            time.sleep(0.5)

        # 09:00:01 ~ 09:00:35, 가상화폐 보유중인 경우 (현재가 < 목표가)이면 전량 매도 (시장가)
        while (state == 1 or state == 3) and buy_date == 0 and reset_time - datetime.timedelta(days=1) + datetime.timedelta(seconds=1) <= now < reset_time - datetime.timedelta(days=1) + datetime.timedelta(seconds=35):
            now = datetime.datetime.now()
            current_price = pyupbit.get_current_price(ticker)
            if current_price < target:
                sell_all_cnt += 1
                if sell_all_cnt == 2:
                    unit = upbit.get_balance(ticker[4:])
                    if unit:
                        upbit.sell_market_order(ticker, unit)
                        post_message(myToken, "#coin", "현재가 < 목표가 전량 매도")
                    state = 0
            else:
                buy_date = 1  # 금일 매수한 걸로 변경

            time.sleep(0.5)

        # 가상화폐 매수전인 경우
        if state == 0:
            # 목표가 도달 시 매수 (지정가)
            if current_price >= target:
                krw = upbit.get_balance("KRW")
                upbit.buy_limit_order(
                    ticker, buy_price, krw / buy_price * 0.9995)
                post_message(myToken, "#coin", str(target) + " 도달 매수 요청")
                state, buy_date = 1, 1

        # 가상화폐 미체결/보유중인 경우
        elif state == 1:
            unit = upbit.get_balance(ticker[4:])
            max_rate = max(max_rate, current_price / target)
            if unit and isinstance(unit, float) and unit >= 1:
                # 상승장인 경우, +18% 지정가 or -11% 지정가 매도
                if bull:
                    if current_price >= target * 1.18:
                        price = math.floor(target * 1.18)
                        upbit.sell_limit_order(ticker, price, unit)
                        post_message(myToken, "#coin", "+18% 매도 요청")
                        state = 2
                    elif current_price <= target * 0.89:
                        price = math.floor(target * 0.89)
                        upbit.sell_limit_order(ticker, price, unit)
                        post_message(myToken, "#coin", "-11% 매도 요청")
                        if sell_chance == 0:
                            sell_chance += 1
                            state = 0
                        else:
                            state = 2
                # 하락장인 경우, +11% 지정가 or -8% 지정가 매도
                else:
                    if current_price >= target * 1.11:
                        price = math.floor(target * 1.11)
                        upbit.sell_limit_order(ticker, price, unit)
                        post_message(myToken, "#coin", "+11% 매도 요청")
                        state = 2
                    elif current_price <= target * 0.92:
                        price = math.floor(target * 0.92)
                        upbit.sell_limit_order(ticker, price, unit)
                        post_message(myToken, "#coin", "-8% 매도 요청")
                        if sell_chance == 0:
                            sell_chance += 1
                            state = 0
                        else:
                            state = 2
                # 0~2% 구간에서 최대상승률 대비 -3% 이상 하락한 경우 지정가 매도
                if (target <= current_price <= target * 1.02) and (current_price <= target * (max_rate - 0.03)):
                    upbit.sell_limit_order(ticker, current_price, unit)
                    post_message(myToken, "#coin", str(
                        current_price) + " (-0.03% 하락) 매도 요청")
                    state = 2

        # 가상화폐 매도한 경우, -30% 하락 시 지정가 매수
        elif state == 0 or state == 2:
            if current_price <= start * 0.7:
                krw = upbit.get_balance("KRW")
                buy_price = math.floor(start * 0.7)
                upbit.buy_limit_order(
                    ticker, buy_price, krw / buy_price * 0.9995)
                post_message(myToken, "#coin", str(
                    buy_price) + " (-30% 하락) 매수 요청")
                state = 3

        # -30%에서 매수한 경우, +14% 상승 시 지정가 매도
        elif state == 3:
            if current_price >= buy_price * 1.14:
                unit = upbit.get_balance(ticker[4:])
                sell_price = math.floor(buy_price * 1.14)
                upbit.sell_limit_order(ticker, sell_price, unit)
                post_message(myToken, "#coin", str(
                    sell_price) + " (+14% 상승) 매도 요청")
                state = 4

        # 금일 거래 종료 시, 08:59:55까지 sleep
        elif state == 4:
            s = (reset_time - now).total_seconds()
            if s - 5 > 0:
                krw = upbit.get_balance("KRW")
                if (isinstance(krw, float)):
                    post_message(myToken, "#coin", "원화: " +
                                 str(round(krw)) + "원, Sleep until next 08:59:55")
                    time.sleep(s - 5)

        time.sleep(0.5)

    # 에러 발생 시 슬랙 알림 전송
    except Exception as e:
        post_message(myToken, "#coin", "error")
        time.sleep(1)
