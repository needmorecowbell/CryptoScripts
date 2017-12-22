import time
from recordBalances import BalanceLogger

if __name__ == "__main__":
    b= BalanceLogger()

    while (True):
        b.getETH()
        b.getTokens()
        b.getBTC()
        b.getNEO() 
        time.sleep(60*30)
