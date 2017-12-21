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


class BalanceLogger():
    """Logs balances of various crypto's public addresses """
    key ="" #etherscan api key
    dbPass= ""
    dbUser= ""
    dbHost= ""
    dbName= ""
    tokens =[]
    eth_addr=""
    btc_address= ""
    neo_address= ""
    etherscan_ratio= 1000000000000000000 #divide by this to get balance formatted to standard

    requestCurrencyConversion='https://api.coinmarketcap.com/v1/ticker/{var[crypto]}/?convert={var[fiat]}'
    total_in_fiat= 0.0



    def __loadFiles(self):
        """Loads data from config.json, tokens.json, and addresses.json
        """
        with open('config/config.json', mode='r') as key_file:#load all config options
            config= json.load(key_file)

            self.key = config['key']
            database_info= config['database']

            self.dbPass= database_info['dbpassword']
            self.dbUser= database_info['dbuser']
            self.dbHost= database_info['dbhost']
            self.dbName= database_info['dbname']

        with open('config/tokens.json', mode='r') as token_file:#load all token options
            self.tokens = json.load(token_file)['token']

        with open('config/addresses.json', mode='r') as addr_file:#load all addresses
            address_data= json.load(addr_file)
            self.eth_addr= address_data['eth']
            self.btc_address= address_data['btc']
            self.neo_address= address_data['neo']



    def getETH(self):
        """Gets Ethereum Balance
        :returns: Dictionary of balances (fiat:coin)
        """
        ether_balance_url=("https://api.etherscan.io/api?module=account&action=balance"
                           "&address={var[ether_addr]}"
                           "&tag=latest"
                           "&apikey={var[key]}")


        #Ethereum
        print("[+] Getting Ethereum Data:")
        reqData = {"ether_addr": self.eth_addr,
                   "key":self.key
                   }
        eth_balance = float(requests.get(ether_balance_url.format(var=reqData)).json()['result'])/self.etherscan_ratio

        convData = {"crypto":"ethereum",
                    "fiat":"USD"
                    }

        usd_per_eth= float(requests.get(self.requestCurrencyConversion.format(var=convData)).json()[0]['price_usd'])
        eth_bal_in_fiat = eth_balance*usd_per_eth

        self.total_in_fiat+=eth_bal_in_fiat


        print("\tCrypto: ethereum ($"+str(usd_per_eth)+")")
        print("\t\tBalance: "+str(eth_balance)+" Coins")
        print("\t\tBalance (USD): $"+str(eth_bal_in_fiat))
        print("")

        return {str(eth_balance):"$"+str(eth_bal_in_fiat)}#returns dict of balances fiat/coin



    def getBTC(self):
        """Gets Bitcoin Balance
        :returns: Dictionary of balances (fiat:coin)
        """

        requestBalanceSatoshi="https://blockchain.info/q/addressbalance/"
        requestAddress="https://blockchain.info/ticker"


        conversionJSON= requests.get(requestAddress).json()
        btc2USD= conversionJSON["USD"]["buy"]


        # BTC
        print("[+] Getting BTC Data:")
        balanceSatoshi =requests.get(requestBalanceSatoshi+self.btc_address)
        btc_balance= float(balanceSatoshi.content) / 100000000.0

        convData = {"crypto":"bitcoin",
                    "fiat":"USD"
                    }


        usd_per_btc= float(requests.get(self.requestCurrencyConversion.format(var=convData)).json()[0]['price_usd'])

        btc_bal_in_fiat= usd_per_btc * btc_balance
        self.total_in_fiat+=btc_bal_in_fiat

        print("\tCrypto: bitcoin ($"+str(usd_per_btc)+")")
        print("\t\tBalance: "+str(btc_balance)+" Tokens")
        print("\t\tBalance (USD): $"+str(btc_bal_in_fiat))
        print("")

        return {str(btc_balance):"$"+str(btc_bal_in_fiat)}#returns dict of balances fiat/coin




    def getTokens(self):
        """Gets Token Balances
        :returns: Dictionary of token balances (tokenName:(fiat:coin))
        """
        # Tokens
        ether_token_url=("https://api.etherscan.io/api?module=account&action=tokenbalance"
                                  "&address={var[ether_addr]}&tag=latest"
                                  "&contractaddress={var[contract_address]}"
                                  "&apikey={var[key]}")

        resultBalances={}
        resultTokens={}
        print("[+] Getting Token Data:")
        for name, contract_addr in self.tokens.items():
            reqData ={"ether_addr": self.eth_addr,
                      "contract_address": contract_addr,
                      "key": self.key
                    }
            token_balance= float(requests.get(ether_token_url.format(var= reqData)).json()['result'])/self.etherscan_ratio

            convData = {"crypto":name,
                        "fiat":"USD"
                        }

            usd_per_token= float(requests.get(self.requestCurrencyConversion.format(var=convData)).json()[0]['price_usd'])
            token_bal_in_fiat = token_balance*usd_per_token

            self.total_in_fiat+=token_bal_in_fiat


            print("\tCrypto: "+ name  + " ($"+str(usd_per_token)+")")
            print("\t\tBalance: "+str(token_balance)+" Tokens")
            print("\t\tBalance (USD): $"+str(token_bal_in_fiat))
            print("")




            resultBalance = {str(token_balance):"$"+str(token_bal_in_fiat)}#adds to dict of balance fiat/usd

            resultTokens.update( {name:resultBalance})

        return resultTokens #returns all checked tokens in a dict






    def getNEO(self):
        """Gets NEO Balance
        :returns: Dictionary of balances (fiat:coin)
        """
        
        print("[+] Getting NEO Data: ")
        requestBalanceNEO= 'https://neoexplorer.co/addresses/'+self.neo_address


        neo_html=requests.get(requestBalanceNEO)
        soup = BeautifulSoup(neo_html.text,'html.parser')

        neo_balances_div= soup.find(class_='balance-list')# find section with wallet  balances
        neo_balances_div=str(neo_balances_div.findAll('strong')[1].contents)# get 'strong' text of balance list ul
        neo_balance= re.findall('\d+',neo_balances_div)# find all digits in contents using regex


        #now that we found the balance, lets get the amount in USD...

        convData = {"crypto":"neo",
                    "fiat":"USD"
                    }

        usd_per_neo= float(requests.get(self.requestCurrencyConversion.format(var=convData)).json()[0]['price_usd'])
        neo_bal_in_fiat = float("".join(neo_balance))*usd_per_neo

        print("\tCrypto: neo ($"+str(usd_per_neo)+")")
        print("\t\tBalance: "+"".join(neo_balance)+" Tokens")
        print("\t\tBalance (USD): $"+str(neo_bal_in_fiat))
        print("")
        self.total_in_fiat+=neo_bal_in_fiat

        return {str(neo_balance):"$"+str(neo_bal_in_fiat)}#returns dict of balances fiat/usd




    def getTotalFiat(self):
        return self.total_in_fiat

    def __init__(self):
        self.__loadFiles()
         # DB INSERT
        timestamp="{:%c}".format(datetime.now())

#        query= "INSERT INTO balances VALUES (null, '"+btc_address+"', '"+str(btcAmount)+"', '"+str(usdAmount) +"', '"+timestamp+"');"
#        db=_mysql.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
        #cur=db.cursor()


        #rowsAffected= cur.execute(query)

#        db.commit();
#        db.close();





if __name__ == "__main__":
    balanceLogger= BalanceLogger()
    balanceLogger.getETH()
    balanceLogger.getTokens()
    balanceLogger.getBTC()
    balanceLogger.getNEO()
    print("Total Balance in Fiat: $"+str(balanceLogger.getTotalFiat()))
