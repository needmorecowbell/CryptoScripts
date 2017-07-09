import requests, json
import MySQLdb

#Get list of dictionaries each containing one currency's data
response = requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
#currencies to log
currencies = ["BTC", "ETH", "LTC", "MIOTA", "DASH"]
#values to log (must be in the same order as sql database)
values = [
    "name", "symbol", "price_usd", "rank", "percent_change_1h",
    "percent_change_24h", "percent_change_7d"
]

#conn = MySQLdb.connect(host= "localhost",
#                  user="root",
#                  passwd="",
#                  db="crypto")
#x = conn.cursor()

try:
    appendedVals = ""
    for crypto in response:
        if (crypto["symbol"] in currencies):
            for item in values:
                if (crypto[item] is not None):
                    appendedVals += ("," + crypto[item])
                    print(item + ": " + crypto[item])
                else:
                    appendedVals += (",")
            appendedVals = appendedVals[1:]  #cleanse  of the first ','
            print(
                """INSERT INTO VALUES """ + appendedVals
            )  #INSERT INTO VALUES (name),(symbol),(price_usd),(rank),(change1h),(change24h),(change7d)
            appendedVals = ""
            #x.execute("""INSERT INTO  VALUES """+appendedVals)
            # conn.commit()

            print("************************\n")
except:
    print("Exception Error")
    #conn.rollback()

#conn.close()
