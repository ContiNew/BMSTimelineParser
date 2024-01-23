import BMSTimelineParser as bp
import pandas as pd
import numpy as np
import math

class Tools:
    @staticmethod
    def to_bitmasked_symbol(laneIdxes)-> int:
        laneIdxes = set(laneIdxes) # 우선 집합으로 바꿈
        notesymbol = 0
        for idx in laneIdxes:
            notesymbol = notesymbol | (1 << idx) # 비트 마스킹
        return notesymbol
    
    @staticmethod
    def get_timediff_series(df:pd.DataFrame)-> pd.Series:
        first_note_timestamp = df['timestamp'].at[0]
        timediff_df =df['timestamp'].drop_duplicates(keep="first")
        timediff_series = (timediff_df - timediff_df.shift(1)).fillna(first_note_timestamp).reset_index(drop=True)
        return timediff_series
    
    @staticmethod
    def get_timediff_series_int(df:pd.DataFrame)-> pd.Series:
        first_note_timestamp = df['timestamp'].apply(math.floor).at[0]
        timediff_df = df['timestamp'].apply(math.floor).drop_duplicates(keep="first")
        timediff_series = (timediff_df - timediff_df.shift(1)).fillna(first_note_timestamp).reset_index(drop=True)
        return timediff_series
        

    
    @staticmethod
    def get_symbolized_notes(df:pd.DataFrame)->pd.Series:
        initial_note = df["laneIdx"].at[0]
        initial_time = df["timestamp"].at[0]
        symbol_candidate = [initial_note]
        symbol_list = []
        for index, row in df.iterrows():
            if(index==0): continue
            if(row['timestamp']==initial_time): 
                symbol_candidate.append(row['laneIdx'])
            else: 
                initial_time = row['timestamp']
                symbol_list.append(Tools.to_bitmasked_symbol(symbol_candidate))
                symbol_candidate.clear()
                symbol_candidate.append(row['laneIdx'])
        
        symbol_list.append(Tools.to_bitmasked_symbol(symbol_candidate))
        return pd.Series(symbol_list).rename("NoteSymbol")
    
    @staticmethod
    def get_symbolized_df(df:pd.DataFrame, isInt:bool=False)->pd.DataFrame:
        timediff= Tools.get_timediff_series(df) if isInt==False else Tools.get_timediff_series_int(df)
        symNotes = Tools.get_symbolized_notes(df)
        notes_df = pd.concat([symNotes, timediff], axis=1)
        return notes_df
    
    @staticmethod
    def get_relative_loc_diff(df:pd.DataFrame)-> pd.Series:
        first_note_location = df['barNum'].at[0] + df['location'].at[0]
        note_loc_diff = (df['barNum'] + df['location']).drop_duplicates(keep="first").reset_index(drop=True)
        loc_diff_series = (note_loc_diff - note_loc_diff.shift(1)).fillna(first_note_location).reset_index(drop=True)
        return loc_diff_series

        

        
        
        
        