import requests, json
#Get list of dictionaries each containing one currency's data
response= requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
#currencies to log
currencies = ["BTC","ETH","LTC","MIOTA","DASH"]
#values to log
values = ["name", "symbol", "price_usd", "rank", "percent_change_1h", "percent_change_24h", "percent_change_7d"]


for crypto in response:
    if(crypto["symbol"] in currencies):
        for item in values:
            if( crypto[item] is not None):
                print( item + ": " + crypto[item])
        print("************************\n")
         
