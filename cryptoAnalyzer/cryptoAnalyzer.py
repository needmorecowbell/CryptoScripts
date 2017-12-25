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
import threading


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

    def _queryWorker(self, cryptoName, lowLimDate, upLimDate, data):
        query= 'SELECT amount_usd, insertedTime FROM balances WHERE crypto="'+cryptoName+'" AND  insertedTime BETWEEN "'+lowLimDate+'" AND "'+upLimDate+'";'

        db=_mysql.connect(host=self.__dbHost, user=self.__dbUser, passwd=self.__dbPass, db=self.__dbName)
        print("Querying "+cryptoName)
        db.query(query)
        queryResult= db.store_result()
        num_rows=queryResult.num_rows()

        amount=[]
        time=[]
        for x in range(0,num_rows) :
            fetched= queryResult.fetch_row(how=1)[0]
            print("Worker["+cryptoName+"]"+str(x)+"/"+str(num_rows-1))



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

        data.append(go.Scatter(x= time,y= amount, name=cryptoName))
       

        db.commit();
        db.close();


    def getAmountInRange(self, cryptoNames, lowLimDate, upLimDate):
        """Creates graphs of amount of crypto in fiat over time,saves to plotly account """

        #query= 'SELECT amount_usd, insertedTime FROM balances WHERE crypto = "'+cryptoName+'" ORDER BY id ASC;'

        data= []
        threads= []
 
        for cryptoName in cryptoNames:
            t = threading.Thread(target=self._queryWorker, args=(cryptoName, lowLimDate, upLimDate, data))
            threads.append(t)
            t.start()

        for thread in threads:
            thread.join()



        timestamp_split= str(lowLimDate).split()
        date_split = timestamp_split[0].split("-")
        time_split = timestamp_split[1].split(":")

        entry_year=int(date_split[0])
        entry_month= int(date_split[1])
        entry_day= int( date_split[2])
        entry_hour=int(time_split[0])
        entry_minute=int(time_split[1])


        minTime= datetime.datetime(year=entry_year, month = entry_month, day= entry_day, hour= entry_hour, minute= entry_minute )
        
        timestamp_split= str(upLimDate).split()
        date_split = timestamp_split[0].split("-")
        time_split = timestamp_split[1].split(":")

        entry_year=int(date_split[0])
        entry_month= int(date_split[1])
        entry_day= int( date_split[2])
        entry_hour=int(time_split[0])
        entry_minute=int(time_split[1])


       
        maxTime= datetime.datetime(year=entry_year, month = entry_month, day= entry_day, hour= entry_hour, minute= entry_minute )



        print("Threads complete")
        print("Plotting...")
        layout = go.Layout( title="Portfolio Balance Over Time",
                            xaxis = dict(
                                range = [self.__toUnixTime(minTime),
                                        self.__toUnixTime(maxTime)],
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
            result = py.iplot(fig, filename=str(filename+"_portfolio_balances"))
        
        else:
            result = plotly.offline.plot(fig, filename=str(filename+"_portfolio_balances.html"))

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
    cryptos= ['ethereum', 'bitcoin', 'omisego','unikoin-gold','basic-attention-token', 'neo','xenon','viuly' ]

    print(c.getAmountInRange(cryptos,"2017-12-20 1:00:00:00", "2017-12-25 23:00:00:00"))








