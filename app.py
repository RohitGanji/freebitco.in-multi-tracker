from flask import Flask, render_template, request, Markup
import pymongo
from datetime import datetime
import requests

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
cookies = [
    # Hidden
    ]
proxies = [
    # Hidden
]

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    client = pymongo.MongoClient("mongodb+srv://username:password@server")
    db = client.BTC
    doc = []
    for x in db.three.find():
        doc.append(x)
    slowredeemable = 0
    instantredeemable = 0
    time = int(datetime.now().timestamp())
    total = 0
    def date(n):
        return int(datetime.fromtimestamp(n).strftime('%d'))
    for i in doc:
        try:
            if i['BTC'] >= float(0.00030000) + i['SLOW']:
                slowredeemable+=(i['BTC']-i['SLOW'])
            if i['BTC'] >= float(0.00030000) + i['INSTANT']:
                instantredeemable+=(i['BTC']-i['INSTANT'])
            total+=(i['BTC'])
            i['BTC'] = "%.8f"%i['BTC']
            i['SLOW'] = "%.8f"%i['SLOW']
            i['INSTANT'] = "%.8f"%i['INSTANT']
        except:
            pass
        if i['STATUS'] and (time < i['NROLL']):
            i['NROLL'] = datetime.fromtimestamp(i['NROLL']).strftime('%H:%M:%S')
        else:
            i['STATUS'] = False
            i['TIME'] = datetime.fromtimestamp(i['TIME']).strftime('%d %H:%M:%S')
        if i['RPB'] and (time < i['NRPB']):
            if date(time) == date(i['NRPB']):
                i['RTODAY'] = True
            else:
                i['RTODAY'] = False
            i['NRPB'] = datetime.fromtimestamp(i['NRPB']).strftime('%H:%M:%S')
        if i['FBB'] and (time < i['NFBB']):
            if date(time) == date(i['NFBB']):
                i['FTODAY'] = True
            else:
                i['FTODAY'] = False
            i['NFBB'] = datetime.fromtimestamp(i['NFBB']).strftime('%H:%M:%S')
    p = requests.get('https://localbitcoins.com/instant-bitcoins/?action=sell&amount=500&currency=INR&country_code=IN&online_provider=ALL_ONLINE&find-offers=Search')   
    try:
        price = float(p.text[p.text.find('class="column-price"'):len(p.text)][p.text[p.text.find('class="column-price"'):len(p.text)].find('\n')+2:p.text[p.text.find('class="column-price"'):len(p.text)].find('INR')].replace(',','').replace(' ',''))
    except:
        price = 0
    totalprice = int(price*total)
    slowprice = int(price*slowredeemable)
    instantprice = int(price*instantredeemable)
    return render_template('index.html', totalprice = totalprice, slowprice = slowprice, instantprice = instantprice, doc = doc, total = "%.8f"%total, instantredeemable = "%.8f"%instantredeemable, slowredeemable = "%.8f"%slowredeemable)

@app.route('/withdraw', methods=['POST'])
def withdraw():
    info = request.form
    amount = info['amount']
    if (bool((info['amount'])=='')):
        amount = str(float(info['btc'])-float(info['fee']))
    headers = {'User-Agent':USER_AGENT,'Cookie': cookies[int(info['id'])]}
    data = {'csrf_token': info['csrf_token'], 'op': 'withdraw', 'type': info['speed'], 'amount': info['amount'], 'withdraw_address': info['withdraw_address'], 'tfa_code': ''}
    return requests.post('https://freebitco.in/', data = data, headers = headers, proxies = proxies[int(info['id'])]).text

if __name__ == '__main__':
    app.run(debug = True)
