
import numpy as np
import pandas as pd

from src.indicators.bbw import bbw

from src.sharedstate import SharedState


class BybitKlineInit:


    def __init__(self, sharedstate: SharedState, recv) -> None:
        self.ss = sharedstate
        self.data = recv['result']['list']

    
    def process(self):
        """
        Used to attain close values and calculate volatility \n
        """

        titles = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
        df = pd.DataFrame(self.data, columns=titles)[::-1]

        self.ss.bybit_klines = df.to_numpy(dtype=float)

        self.ss.volatility_value = bbw(
            arr_in = self.ss.bybit_klines, 
            length = self.ss.bb_length, 
            std = self.ss.bb_std
        )

        self.ss.volatility_value += self.ss.volatility_offset



class BybitKlineHandler:


    def __init__(self, sharedstate: SharedState, data) -> None:
        self.ss = sharedstate
        self.data = data

    
    def process(self):
        """
        Used to attain close values and calculate volatility \n
        If candle close, shift array -1 and add new value \n
        Otherwise, update the most recent value \n
        """

        for candle in self.data:

            time = candle["start"]
            open = candle["open"]
            high = candle["high"]
            low = candle["low"]
            close = candle["close"]
            volume = candle["volume"]
            turnover = candle["turnover"]

            new = np.array([time, open, high, low, close, volume, turnover], dtype=float)

            if candle['confirm'] == True:
                self.ss.bybit_klines = np.append(arr=self.ss.bybit_klines[1:], values=new.reshape(1, 7), axis=0)

            else:
                self.ss.bybit_klines[-1] = new
            
            self.ss.volatility_value = bbw(
                arr_in = self.ss.bybit_klines, 
                length = self.ss.bb_length, 
                std = self.ss.bb_std
            )

            self.ss.volatility_value += self.ss.volatility_offset