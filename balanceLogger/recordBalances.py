#**************************************************************
# Created by: Adam Musciano
# Description: Monitors balances of different cryptocurrencies
#
#
#*************************************************************
import re
import requests
import json
from datetime import datetime
from time import sleep
import _mysql
from bs4 import BeautifulSoup

with open('config.json', mode='r') as key_file:#load all config options
    config= json.load(key_file)
    
    key = config['key'] 
    database_info= config['database']
    
    dbPass= database_info['dbpassword']
    dbUser= database_info['dbuser']
    dbHost= database_info['dbhost']
    dbName= database_info['dbname']

with open('tokens.json', mode='r') as token_file:#load all token options
    tokens = json.load(token_file)['token']

with open('addresses.json', mode='r') as addr_file:#load all addresses
    address_data= json.load(addr_file)
    eth_addr= address_data['eth']
    btc_address= address_data['btc']
    neo_address= address_data['neo']


etherscan_ratio= 1000000000000000000

btcAmount=0.0
usdAmount=0.0

balanceSatoshi=""

total_in_fiat= 0.0


requestBalanceSatoshi="https://blockchain.info/q/addressbalance/"
requestAddress="https://blockchain.info/ticker"



requestCurrencyConversion='https://api.coinmarketcap.com/v1/ticker/{var[crypto]}/?convert={var[fiat]}'

conversionJSON= requests.get(requestAddress).json()
btc2USD= conversionJSON["USD"]["buy"]

ether_token_url=("https://api.etherscan.io/api?module=account&action=tokenbalance"
                                  "&address={var[ether_addr]}&tag=latest"
                                  "&contractaddress={var[contract_address]}"
                                  "&apikey={var[key]}")

ether_balance_url=("https://api.etherscan.io/api?module=account&action=balance"
                   "&address={var[ether_addr]}"
                   "&tag=latest"
                   "&apikey={var[key]}")



#Ethereum
print("[+] Getting Ethereum Data:")
reqData = {"ether_addr": eth_addr,
           "key":key
           }
eth_balance = float(requests.get(ether_balance_url.format(var=reqData)).json()['result'])/etherscan_ratio

convData = {"crypto":"ethereum",
            "fiat":"USD"
            }

usd_per_eth= float(requests.get(requestCurrencyConversion.format(var=convData)).json()[0]['price_usd'])
eth_bal_in_fiat = eth_balance*usd_per_eth

print("Crypto: Ethereum ($"+str(usd_per_eth)+")\t"+str(eth_balance)+" Coins\t$"+str(eth_bal_in_fiat))

total_in_fiat+=eth_bal_in_fiat


# Tokens
print("[+] Getting Token Data:")
for name, contract_addr in tokens.items():
    reqData ={"ether_addr": eth_addr,
              "contract_address": contract_addr,
              "key": key
              }
    token_balance= float(requests.get(ether_token_url.format(var= reqData)).json()['result'])/etherscan_ratio

    convData = {"crypto":name,
                "fiat":"USD"
                }

    usd_per_token= float(requests.get(requestCurrencyConversion.format(var=convData)).json()[0]['price_usd'])
    token_bal_in_fiat = token_balance*usd_per_token
    print("Crypto: "+ name +"($"+str(usd_per_token)+")\t"+str(token_balance)+" Tokens\t$"+str(token_bal_in_fiat))

    total_in_fiat+=token_bal_in_fiat



# BTC
print("[+] Getting BTC Data:")
balanceSatoshi =requests.get(requestBalanceSatoshi+btc_address)
btc_balance= float(balanceSatoshi.content) / 100000000.0

convData = {"crypto":"bitcoin",
            "fiat":"USD"
            }


usd_per_btc= float(requests.get(requestCurrencyConversion.format(var=convData)).json()[0]['price_usd'])
 
btc_bal_in_fiat= usd_per_btc * btc_balance
print("Crypto: bitcoin($"+str(usd_per_btc)+")\t"+str(btc_balance)+" Tokens\t$"+str(btc_bal_in_fiat))



#NEO
print("[+] Getting NEO Data: ")
requestBalanceNEO= 'https://neoexplorer.co/addresses/'+neo_address


neo_html=requests.get(requestBalanceNEO)
soup = BeautifulSoup(neo_html.text,'html.parser')

neo_balances_div= soup.find(class_='balance-list')# find section with wallet  balances
neo_balances_div=str(neo_balances_div.findAll('strong')[1].contents)# get 'strong' text of balance list ul
neo_balance= re.findall('\d+',neo_balances_div)# find all digits in contents using regex


#now that we found the balance, lets get the amount in USD...

convData = {"crypto":"neo",
            "fiat":"USD"
            }

usd_per_neo= float(requests.get(requestCurrencyConversion.format(var=convData)).json()[0]['price_usd'])
neo_bal_in_fiat = float("".join(neo_balance))*usd_per_neo

print("Crypto: neo ($"+str(usd_per_neo)+")\t"+str(token_balance)+" Tokens\t$"+str(neo_bal_in_fiat))

total_in_fiat+=neo_bal_in_fiat


print("Total Balance in Fiat: $"+str(total_in_fiat))

# DB INSERT
timestamp="{:%c}".format(datetime.now())

query= "INSERT INTO balances VALUES (null, '"+btc_address+"', '"+str(btcAmount)+"', '"+str(usdAmount) +"', '"+timestamp+"');"
db=_mysql.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
#cur=db.cursor()


#rowsAffected= cur.execute(query)

db.commit();
db.close();
    




