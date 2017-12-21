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

requestUSDConversion='https://blockchain.info/tobtc?currency=USD&value='
requestBalanceSatoshi="https://blockchain.info/q/addressbalance/"
requestAddress="https://blockchain.info/ticker"

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
print("Smybol: ETH\t"+str(eth_balance)+" Coins")



# Tokens
print("[+] Getting Token Data:")
for name, contract_addr in tokens.items():
    reqData ={"ether_addr": eth_addr,
              "contract_address": contract_addr,
              "key": key
              }
    token_balance= float(requests.get(ether_token_url.format(var= reqData)).json()['result'])/etherscan_ratio
    print("Symbol: "+ name.upper() +"\t"+str(token_balance)+" Tokens")



# BTC
print("[+] Getting BTC Data:")
balanceSatoshi =requests.get(requestBalanceSatoshi+btc_address)

btcAmount= float(balanceSatoshi.content) / 100000000.0
usdAmount= float(btc2USD*btcAmount)
print("Symbol: BTC\t"+str(btcAmount)+" Coins")


#NEO
print("[+] Getting NEO Data: ")
requestBalanceNEO= 'https://neoexplorer.co/addresses/'+neo_address


neo_html=requests.get(requestBalanceNEO)
soup = BeautifulSoup(neo_html.text,'html.parser')

neo_balances_div= soup.find(class_='balance-list')# find section with wallet  balances
neo_balances_div=str(neo_balances_div.findAll('strong')[1].contents)# get 'strong' text of balance list ul
neo_balance= re.findall('\d+',neo_balances_div)# find all digits in contents using regex

print("Symbol: NEO\t"+"".join(neo_balance)+" Coins")




# DB INSERT
timestamp="{:%c}".format(datetime.now())

query= "INSERT INTO balances VALUES (null, '"+btc_address+"', '"+str(btcAmount)+"', '"+str(usdAmount) +"', '"+timestamp+"');"
db=_mysql.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
#cur=db.cursor()


#rowsAffected= cur.execute(query)

db.commit();
db.close();
    




