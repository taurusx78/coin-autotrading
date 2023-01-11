# Coin Autotrading
가상화폐 자동매매를 위한 Python 프로그램이다.
<br><br>

## 설명
Python을 이용한 가상화폐 자동매매 프로그램으로 목표 매수/매도가 도달 시 매매를 진행하는 역할을 한다.<br>
1. 클라우드 서버를 이용해 24시간 내내 프로그램을 가동시키고 거래를 진행한다.
2. 일일 목표가 갱신, 목표가 도달 및 매매 진행, 프로그램 에러 발생 시 Slack을 통해 알림을 받는다.
<br>

## 거래 전략
<div>
  <p>[예시]</p><br>
  <img src="https://user-images.githubusercontent.com/56622731/211847406-6a8d8329-a283-4b1d-94f3-573755cad6d2.png" width="500"/>
</div><br>

- 주식 투자 시 자주 사용되는 변동성 돌파 전략은 상승장에서 설정된 목표가 도달 시 매수하고 종가에 매도하는 단순한 방식이었기 때문에, 주식 시장과 달리 변동성이 매우 큰 가상화폐 시장에 적용할 경우 오히려 큰 손실을 입게 되는 문제 발생한다.
- 매수 후 종가에 매도하는 대신 매수가에서 일정 기준 이상 상승/하락 시 매도한다면 좀 더 높은 수익률을 달성할 수 있을 것이라 판단, 매도 기준을 설정하기 위한 변수를 추가해 백테스팅을 진행하고 그 기준을 프로그램에 적용하였다.
- (참고) https://wikidocs.net/book/1665
<br>

## 한계
백테스팅을 통해 매매 기준을 잘 설정했다 하더라도 결국 해당 테스트는 가상화폐의 과거 데이터를 바탕으로 진행되었기 때문에, 미래에도 이 기준에서 좋은 수익을 낼 것이라는 것을 보장해주지 못한다. 즉, 가상화폐 시장 분위기가 변동되면 손실을 입게될 수도 있다.
<br><br><br>

## 기술스택
- Python
- Naver Cloud Platform (NCP)
- Slack
<br>

## Open API
- [Upbit Open API](https://upbit.com/service_center/open_api_guide)
<br>

## Ubuntu 서버 명령어
```bash
# 백그라운드로 프로그램 실행
nohup python3 파일명.py > output.log &

# 프로그램 실행 여부 확인 (PID 확인 가능)
ps ax | grep .py

# 프로그램 종료
kill -9 PID
```
<br>

## 파일 업로드
내 PC에서 우분투 서버로 파일을 업로드하려면, cmd 창에서 다음 코드를 입력하면 된다.
```bash
scp -P 포트번호 파일경로\파일명.py root@우분투서버고정IP:/업로드폴더명

# 예시
# scp -P 1028 C:\Users\JIN\PycharmProjects\autotrading\Main\autotrading.py root@106.10.39.203:/home
```
<br>
