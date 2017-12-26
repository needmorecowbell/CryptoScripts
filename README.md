# CryptoScripts
A Collection of scripts designed for the purpose of crypto currency analysis, trend spotting, and automation.

------


## Balance Logger
Balance Logger calls various crypto apis/websites to get the balances of all your cryptocurrencies in one place. Helpful for automatically getting the total balance of your crypto portfolio. Supports ERC20 Tokens


*To Do*
  * Add more contract addresses so people don't have to manually


-------

## Crypto Analyzer

Crypto Analyzer takes information from the Balance Logger, and provides graphs of the information on plotly in online mode, or locally in offline mode.

**NOTE:** You do not need to fill in the config settings for plotly unless you are using online mode. 

*To Do*
  * Make more functions that provide graphs in plotly
-------

## Crypto Logger
This program scrapes crypto data using the coinmarketcap api, then sends it to a mysql database.

![Alt text](/res/cryptoLoggerOutput.png)

*To Do*

  * Config file for choice in currency logging
  * Decide whether it should be a script that runs on cron, or does scheduling by itself
------

