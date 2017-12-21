import requests

requestAddress="https://blockchain.info/ticker"


content = requests.get(requestAddress).json()

print (content["USD"]["buy"])
