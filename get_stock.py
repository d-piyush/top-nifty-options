import requests
import threading, time
from datetime import datetime


WAIT_TIME_SECONDS = 5 * 60

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',}
URL = 'https://www.nseindia.com/api/liveEquity-derivatives?index=nse50_opt' 

previous_call_list = []
previous_put_list = []

def fetch_latest():
    r = requests.get(URL, headers=HEADERS)
    stock_list = r.json().get('data')
    global previous_put_list, previous_call_list

    put_list = []
    call_list = []

    for stock in stock_list :
        if stock.get('optionType') == 'Call':
            call_list.append(stock)
        elif stock.get('optionType') == 'Put':
            put_list.append(stock)

    put_list = sorted(put_list, key=lambda k: k['totalTurnover'], reverse=True)
    call_list = sorted(call_list, key=lambda k: k['totalTurnover'], reverse=True)

    for put in put_list:
        for old_put in previous_put_list:
            if put.get('identifier') == old_put.get('identifier'):
                try:
                    put['roc'] = ((put.get('totalTurnover')/old_put.get('totalTurnover')) - 1) * 100
                    break
                except ZeroDivisionError:
                    pass

    for call in call_list:
        for old_call in previous_call_list:
            if call.get('identifier') == old_call.get('identifier'):
                try:
                    call['roc'] = ((call.get('totalTurnover')/old_call.get('totalTurnover')) - 1) * 100
                    break
                except ZeroDivisionError:
                    pass

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    print('Current Time: ', timestampStr)
    print('############################CALL Table##############################')
    print('Strike price | Total turnover | ROC') 
    for i in range(10):
        strike_price = call_list[i].get('strikePrice')
        total_turnover = call_list[i].get('totalTurnover')
        roc = call_list[i].get('roc', 'NA')
        print(strike_price, " | ", total_turnover, " | ", roc)

    print('\n\n')
    print('############################PUT Table##############################')
    print('Strike price | Total turnover | ROC') 
    for i in range(10):
        strike_price = put_list[i].get('strikePrice')
        total_turnover = put_list[i].get('totalTurnover')
        roc = put_list[i].get('roc', 'NA')
        print(strike_price, " | ", total_turnover, " | ", roc)

    print('##################################################################')
    print('\n\n\n\n\n')

    previous_call_list = call_list
    previous_put_list = put_list
    
        
    


fetch_latest()
ticker = threading.Event()
while not ticker.wait(WAIT_TIME_SECONDS):
    fetch_latest()


