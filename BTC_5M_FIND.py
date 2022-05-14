import ccxt
from datetime import datetime, timedelta
import pandas as pd
import requests
from time import time, sleep
import time

# 비트코인 5분봉이 증가할 때 알트코인들로 단타매매를 한다.


interval = "5m"  # 매수 기준 ( 급등 분봉 기준)
percent = 0.004  # 전꺼 기준 2.5% 급등하면 사자. ( 매수 기준.)


binance_account = ccxt.binance()
# =============================================계정 세팅=================================================================

# --------------------------slack bot----------------------------------
mytoken = "token_number"
channel = "#binance_stock"  # 채널설정


def post_message(token, channel, text):
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer " + token},
        data={"channel": channel, "text": text},
    )
    print(response)


# --------------------------slack bot----------------------------------


# --------------------------running time----------------------------------
end_time = datetime.now() + timedelta(days=30)  # 1달
# --------------------------running time----------------------------------

print("---------------------------------------------------------------------------------------------------------")
print("비트코인 5분봉 상승 시각 : ", datetime.now())  # 자동매매 시작

# --------------------------slack bot----------------------------------
slack_text = "비트코인 5분봉 증가 시각 FIND 프로그램 시작 : " + str(datetime.now())
post_message(mytoken, channel, slack_text)
# --------------------------slack bot----------------------------------


# ----------------------------------------------------------------------------setting-------------------------------------------------------------------------------------------------

# --------------------------------- coin 선택--------------------------------------------------
error_count = 0
count = 5  # 데이터개수
target_time=[]
target_time_percent=[]

coin ='BTC/USDT'
pivot = 0
while datetime.now() < end_time :
    try:
        print(' 돌아가고 있는중...')
        
        df_close = []
        df_date = []
        df_open = []
        condition = 0
        # --------------------------- 데이터 가져오기 -------------------------------------
        ohlcvs = binance_account.fetch_ohlcv(coin, timeframe=interval)  # 5분봉 가져오기

        for ohlc in ohlcvs[len(ohlcvs) - count :]:
            df_date.append(
                datetime.fromtimestamp(ohlc[0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            )  # 시간넣음
            df_close.append(ohlc[4])  # 종가넣음
            df_open.append(ohlc[1]) # 시가넣음

        # --------------------------- 데이터 가져오기 -------------------------------------

        # --------------------------- target list 생성 -------------------------------------
        target = []
        blue_or_red = []

        for i in range(1, len(df_close)):
            target.append((df_close[i] / df_close[i - 1]) - 1)
            blue_or_red.append( (df_close[i] - df_open[i]) / df_open[i] ) # (종가-시가)/시가

        target.insert(0, 0)
        blue_or_red.insert(0, 0)
        # --------------------------- target list 생성 -------------------------------------
        # --------------------------- 데이터프레임 생성 -------------------------------------
        new = pd.DataFrame(
            {
                "df_date": df_date,
                "df_close": df_close,
                "target": target,
                "blue_or_red": blue_or_red,  # 양수면 양봉(red), 음수면 음봉(blue)
            }
        )
        # --------------------------- 데이터프레임 생성 ------------------------------------

        # --------------------------- 조건 생성 -------------------------------------
        MA5 = 0
        for ohlc in ohlcvs[len(ohlcvs) - 5 :]:
            MA5 = MA5 + ohlc[4]
        MA5 = MA5 / 5

        MA5_1 = 0
        for ohlc in ohlcvs[len(ohlcvs) - 6 : len(ohlcvs) - 1]:
            MA5_1 = MA5_1 + ohlc[4]
        MA5_1 = MA5_1 / 5

        MA5_2 = 0
        for ohlc in ohlcvs[len(ohlcvs) - 7 : len(ohlcvs) - 2]:
            MA5_2 = MA5_2 + ohlc[4]
        MA5_2 = MA5_2 / 5
        # 3분봉에서 5이평선이 꺽이면 매도

        # MA5가 가장 최근의 이동평균선 값
        # first = MA5_1 - MA5_2
        # second = MA5 - MA5_1

        # 5분봉이 꺽이는 순간.
        condition =  (MA5 > MA5_1) and (MA5_1 < MA5_2 )

        # 양봉이 3개이면
        # condition = (
        #     (new.blue_or_red[2] > 0)
        #     and (new.blue_or_red[3] > 0)
        #     and (new.blue_or_red[4] > 0)
        # )
        condition_2 = (new.blue_or_red[4] > 0.004)


        if condition > 0:
            slack_text = "비트코인 5분봉 5MA 증가 시각 : " + str(datetime.now()) + '\n' + "트레이딩을 해볼 타이밍입니다."
            post_message(mytoken, channel, slack_text)
            
            target_time.append(datetime.now())
            slack_text = "30초 쉬고 다시 CHECK, 1번만 울려도 확인, 애메하면 2번째 울렸을때 또확인."
            post_message(mytoken, channel, slack_text)
            time.sleep(30)

        if condition_2 >0:
            slack_text = "비트코인 5분봉 0.4프로 이상 오른 시각 : " + str(datetime.now())+ '\n' + "트레이딩을 해볼 타이밍입니다."
            post_message(mytoken, channel, slack_text)
            
            target_time_percent.append(datetime.now())
            slack_text = "30초 쉬고 다시 CHECK, 1번만 울려도 확인, 애메하면 2번째 울렸을때 또확인."
            post_message(mytoken, channel, slack_text)
            time.sleep(30)


        print('비트코인 5분봉 5MA 증가 조건: ',condition)
        print("비트코인 5분봉 0.4프로 이상 증가 조건: ",condition_2)
        # --------------------------- 조건 생성 -------------------------------------
        # if condition > 0:  # 급상승 코인을 찾는 순간 break.Fe
        #     break
      

        # time.sleep(0.05)  # 일시정지를 걸어주니 에러가 사라졌다..

    except Exception as err:
        print("에러")
        error_count = error_count + 1
        sleep(1)

    
    # balance = binance_account.fetch_balance()  # 내가 가지고 있는 BALANCE

    # 여기까지는 변형 완료.
    # --------------------------------- coin 선택--------------------------------------------------

print('---------------------------------------------------------------------------')
print('끝난시각: ', datetime.now())


slack_text = '끝난시각: '+ datetime.now()
post_message(mytoken, channel, slack_text)



a = "5분봉 증가 시각: "
for i in range(0, len(target_time)):
    a = a + f" {target_time[i]}"
print(a)
# --------------------------slack bot----------------------------------
slack_text = a
post_message(mytoken, channel, slack_text)
# --------------------------slack bot----------------------------------


b = "비트코인 0.4프로 이상 오른 시각: "
for i in range(0, len(target_time_percent)):
    b = b + f" {target_time_percent[i]}"
print(b)
# --------------------------slack bot----------------------------------
slack_text = b
post_message(mytoken, channel, slack_text)
# --------------------------slack bot----------------------------------