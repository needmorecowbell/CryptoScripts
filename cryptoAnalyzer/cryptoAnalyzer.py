#**************************************************************
# Created by: Adam Musciano
# Description: Monitors balances of different cryptocurrencies
#
#
#*************************************************************
#   mysql find balance and time for crypto > select amount_usd, insertedTime from balances where crypto="ethereum" ORDER BY id ASC

import json
import datetime
from time import sleep
import _mysql

import pandas as pd
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
import plotly

class CryptoAnalyzer():
    """Creates graphs and spots trends of various crypto's using retrieved data from balanceLogger """
    __dbPass= ""
    __dbUser= ""
    __dbHost= ""
    __dbName= ""
    __plotlyUsername= ""
    __plotlyKey = ""
    
    isOnline= False

    def __loadFiles(self):
        """Loads data from config.json
        """
        with open('../config/config.json', mode='r') as config_file:#load all config options
            config= json.load(config_file)

            plotly_info = config['plotly']
            self.__plotlyUsername= plotly_info['username']
            self.__plotlyKey = plotly_info['key']


            database_info= config['database']
            self.__dbPass= database_info['dbpassword']
            self.__dbUser= database_info['dbuser']
            self.__dbHost= database_info['dbhost']
            self.__dbName= database_info['dbname']

    def __toUnixTime(self, dt):
        epoch =  datetime.datetime.utcfromtimestamp(0)
        return (dt - epoch).total_seconds() * 1000



    def getAmountInRange(self, cryptoName, lowLimDate, upLimDate):
        """Creates graphs of amount of crypto in fiat over time,saves to plotly account """

        #query= 'SELECT amount_usd, insertedTime FROM balances WHERE crypto = "'+cryptoName+'" ORDER BY id ASC;'
        query= 'SELECT amount_usd, insertedTime FROM balances WHERE crypto="'+cryptoName+'" AND  insertedTime BETWEEN "'+lowLimDate+'" AND "'+upLimDate+'";'

        db=_mysql.connect(host=self.__dbHost, user=self.__dbUser, passwd=self.__dbPass, db=self.__dbName)

        db.query(query)
        queryResult= db.store_result()
        num_rows=queryResult.num_rows()

        amount=[]
        time=[]
        for x in range(0,num_rows) :
            fetched= queryResult.fetch_row(how=1)[0]



            timestamp_split= str(fetched["insertedTime"].decode('utf-8')).split()
            date_split = timestamp_split[0].split("-")
            time_split = timestamp_split[1].split(":")

            entry_year=int(date_split[0])
            entry_month= int(date_split[1])
            entry_day= int( date_split[2])
            entry_hour=int(time_split[0])
            entry_minute=int(time_split[1])


            time.append(datetime.datetime(year=entry_year, month = entry_month, day= entry_day, hour= entry_hour, minute= entry_minute ))
            amount.append(float(fetched["amount_usd"]))

            sleep(1)


        data= []

        data.append(go.Scatter(x= time,y= amount))

        layout = go.Layout(title=cryptoName+" Balance Over Time",
                            xaxis = dict(
                                range = [self.__toUnixTime(time[0]),
                                        self.__toUnixTime(time[-1])],
                                title= "Time",
                                type=  "date"

                                ),
                            yaxis = dict(
                                title= "Balance USD"
                            )

        )

        fig = go.Figure(data= data, layout = layout)
        filename=str(datetime.datetime.now().strftime('%m-%d-%Y_%H-%M'))
        if(self.isOnline):
            result = py.iplot(fig, filename=str(filename+"_"+cryptoName))
        
        else:
            result = plotly.offline.plot(fig, filename=str(filename+"_"+cryptoName+".html"))

        db.commit();
        db.close();
        return result 



    def getTotalFiat(self):
        pass#return self.total_in_fiat

    def __init__(self, online= False):
        self.__loadFiles()
        self.isOnline= online
        if (self.isOnline):
            plotly.tools.set_credentials_file(username=self.__plotlyUsername, api_key=self.__plotlyKey)





if __name__ == "__main__":
    c = CryptoAnalyzer()
    print(c.getAmountInRange("ethereum","2017-12-21 16:00:00:00", "2017-12-23 22:30:00:00"))
    print(c.getAmountInRange("omisego","2017-12-21 16:00:00:00", "2017-12-23 22:30:00:00"))
    print(c.getAmountInRange("bitcoin","2017-12-21 16:00:00:00", "2017-12-23 22:30:00:00"))
    print(c.getAmountInRange("unikoin-gold","2017-12-21 16:00:00:00", "2017-12-23 22:30:00:00"))
    print(c.getAmountInRange("basic-attention-token","2017-12-21 16:00:00:00", "2017-12-23 22:30:00:00"))
    print(c.getAmountInRange("neo","2017-12-21 16:00:00:00", "2017-12-23 22:30:00:00"))








