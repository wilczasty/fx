
import pandas_ta as ta
import pandas as pd
import numpy as np
import datamanager as dm

class Strategy():
    name = 'BASE CLASS'
    description = 'Base class'
    def __init__(self):
        self.id = None
    def add_datapoints(self, df): pass

    def store(self):
        self.id = dm.get_timestamp()
        dm.store_strategy(self,data=[self.id,self.name,self.description],filename=self.id)

class MultiIndicators(Strategy):
    name = 'MULTI_INDI'
    description = 'RSI + Slope + BB + Aroon + Ema50 + EMA200 + daily change'
    input_count = 7
    def __init__(self):
        super().__init__()

    def add_datapoints(self,df:pd.DataFrame):
        
        df['OpenShift'] = df['Open'].shift(-1)
        df['RSI'] = ta.rsi(df['Close'],14)/100
        df['ATR'] = ta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=21)
        df['Slope'] = ta.slope(close = df['Close'], length = 10) / df['ATR']
        ar = ta.aroon(high=df['High'], low=df['Low'], length=14)
        bb = ta.bbands(close=df['Close'], length=20)
        df['BBOsc'] = bb['BBP_20_2.0']
        df['Aroon'] = ar['AROONOSC_14'] / 100
        df['EMA50'] = (df['Close'] - ta.ema(df['Close'],50)) / df['ATR']
        df['EMA200'] = (df['Close'] - ta.ema(df['Close'],200)) / df['ATR']
        df['Change'] = (df['Close']-df['Close'].shift(1)) / df['Close']
        df['Input'] = df[['Change','Slope','RSI','BBOsc','Aroon','EMA50','EMA200']].values.tolist()
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        df.dropna(inplace = True)
        return df

class MultiIndicators2(Strategy):
    name = 'MULTI_INDI_ATR'
    description = 'RSI + Slope + BB + Aroon + Ema50 + EMA200 + daily change by ATR'
    input_count = 7
    def __init__(self):
        super().__init__()

    def add_datapoints(self,df:pd.DataFrame):
        df['OpenShift'] = df['Open'].shift(-1)
        df['RSI'] = ta.rsi(df['Close'],14)/100
        df['ATR'] = ta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=21)
        df['Slope'] = ta.slope(close = df['Close'], length = 10) / df['ATR']
        ar = ta.aroon(high=df['High'], low=df['Low'], length=14)
        bb = ta.bbands(close=df['Close'], length=20)
        df['BBOsc'] = bb['BBP_20_2.0']
        df['Aroon'] = ar['AROONOSC_14'] / 100
        df['EMA50'] = (df['Close'] - ta.ema(df['Close'],50)) / df['ATR']
        df['EMA200'] = (df['Close'] - ta.ema(df['Close'],200)) / df['ATR']
        df['Change'] = (df['Close']-df['Close'].shift(1)) / df['ATR']
        df['Input'] = df[['Change','Slope','RSI','BBOsc','Aroon','EMA50','EMA200']].values.tolist()
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        df.dropna(inplace = True)
        return df

class MovingAverages(Strategy):
    name = 'MOVINGAVGv2'
    description = 'EMA 9, 13, 21, 50, 100, 150, 200'
    input_count = 7
    def __init__(self):
        super().__init__()

    def add_datapoints(self,df:pd.DataFrame):
        df['OpenShift'] = df['Open'].shift(-1)
        df['ATR'] = ta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=21)
        df['EMA9'] = (df['Close'] - ta.ema(df['Close'],9)) / df['ATR']
        df['EMA13'] = (df['Close'] - ta.ema(df['Close'],13)) / df['ATR']
        df['EMA21'] = (df['Close'] - ta.ema(df['Close'],21)) / df['ATR']
        df['EMA50'] = (df['Close'] - ta.ema(df['Close'],50)) / df['ATR']
        df['EMA100'] = (df['Close'] - ta.ema(df['Close'],100)) / df['ATR']
        df['EMA150'] = (df['Close'] - ta.ema(df['Close'],150)) / df['ATR']
        df['EMA200'] = (df['Close'] - ta.ema(df['Close'],200)) / df['ATR']
        df['Input'] = df[['EMA9','EMA21','EMA21','EMA50','EMA100','EMA150','EMA200']].values.tolist()
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        df.dropna(inplace = True)
        return df

class RSI_ADX(Strategy):
    name = 'RSIADX'
    description = 'rsi and adx'
    input_count = 4
    def __init__(self):
        super().__init__()

    def add_datapoints(self,df:pd.DataFrame):
        df['OpenShift'] = df['Open'].shift(-1)
        df['RSI'] = ta.rsi(df['Close'],14)/100
        adx = ta.adx(high=df['High'], low=df['Low'], close=df['Close'], length=14)/100
        df['ADX'] = adx['ADX_14']
        df['ADXPLUS'] = adx['DMP_14']
        df['ADXMINUS'] = adx['DMN_14']
        df['Input'] = df[['RSI','ADX','ADXPLUS','ADXMINUS']].values.tolist()
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        df.dropna(inplace = True)
        return df

class ClearPrice(Strategy):
    name = 'CLEARPRICEv3'
    description = 'Using price calculations as input'
    input_count = 9
    def __init__(self):
        super().__init__()

    def add_datapoints(self,df:pd.DataFrame):
        df['OpenShift'] = df['Open'].shift(-1)
        df['ATR'] = ta.atr(high=df['High'], low=df['Low'], close=df['Close'], length=21)
        df['EMA200'] = (df['Close'] - ta.ema(df['Close'],200)) / df['ATR']
        df['HL1'] = (df['High'] - df['Low']) / df['ATR']
        df['HL2'] = (df['High'].shift(1) - df['Low'].shift(1)) / df['ATR']
        df['HL3'] = (df['High'].shift(2) - df['Low'].shift(2)) / df['ATR']
        df['OC1'] = (df['Open'] - df['Close']) / df['ATR']
        df['OC2'] = (df['Open'].shift(1) - df['Close'].shift(1)) / df['ATR']
        df['OC3'] = (df['Open'].shift(2) - df['Close'].shift(2)) / df['ATR']
        df['CC1'] = (df['Close'] - df['Close'].shift(1)) / df['ATR']
        df['CC2'] = (df['Close'].shift(1) - df['Close'].shift(2)) / df['ATR']
        
        df['Input'] = df[['EMA200','HL1','HL2','HL3','OC1','OC2','OC3','CC1','CC2']].values.tolist()
        df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
        df.dropna(inplace = True)
        return df