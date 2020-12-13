import pandas as pd
import numpy as np

from pandas.api.indexers import BaseIndexer
from typing import Optional

class MyStartOfDayIndexer(BaseIndexer):
    """
    calculates the rolling window bounds based off [(current-offset).floor('d'), current)
    - the window begins at the START of the first day in the range (rather than offset away)

    - for a RollingGroupby the index_array is calculated automatically for each group
    - for a regular Rolling, we can pass datetime indices as the 'on' parameter

    - NOT closed on the left means the first nanosecond of the day isn't included
    (rather than the first entry)

    params:
    offset - size of the rolling window (determines start day)

    References:
    pandas/core/window/indexers.py
    pandas/core/window/rolling.py
    https://github.com/pandas-dev/pandas/pull/29878
    """
    def  __init__(self,
                  index_array: Optional[np.ndarray] = None,
                  window_size: int=0,
                  offset=None,
                  **kwargs,):
        super().__init__(index_array, window_size,**kwargs)
        
        self.offset=pd.Timedelta(offset).delta

        if hasattr(self, 'on'):
            if self.index_array is None and self.on is not None:
                self.index_array = self.on.astype('int64')

        # not sure why self.closed isn't passed to get_window_bounds as closed?
        if hasattr(self, 'closed'):
            if self.closed is None:
                self.closed = 'left'
        else:
            self.closed = 'left'
           
    def get_window_bounds(self, num_values, min_periods, center, closed):
        if closed is None:
            closed = self.closed
            
        right_closed = closed in ['right', 'both']
        left_closed = closed in ['left', 'both']
        
        start = np.empty(num_values, dtype='int64')
        end = np.empty(num_values, dtype='int64')
        start[0] = 0
        end[0] = right_closed # 0 or 1
        
        for i in range(1,num_values):
            start[i] = i

            # floor the start datetime to the start of a day
            # using the integer representation of datetime in nanoseconds
            # assumes all days are the same length and no additional offset from the first day
            start_bound = pd.Timedelta('1d').value *\
                int((self.index_array[i]-self.offset) / pd.Timedelta('1d').value)

            start_bound -= left_closed # 0 or -1
            
            for j in range(start[i-1], i):
                if self.index_array[j] > start_bound:
                    start[i] = j
                    break
            
            end[i] = i + right_closed # 0 or +1
            
        return start, end

def test_my_indexer():
    df = pd.DataFrame([['2020-01-01',1],
                       ['2020-01-01 12:00:00',1],
                       ['2020-01-02',1],
                       ['2020-01-02 12:00:00',1],
                       ['2020-01-03',1],
                       ['2020-01-03 12:00:00',1]],
                      columns=['timestamp','value'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(df)
    
    # regular 1d rolling window (max 2 entries in the last 24h since they are in 12h increments)
    print(df.rolling('1d',closed='left', on='timestamp').sum())
    
    # 1d rolling window from the start of the previous day
    two_day_sum = df.rolling(MyStartOfDayIndexer(on=df.timestamp,offset='1d',closed='left')).sum()
    print(two_day_sum)
    assert(two_day_sum['value'].tolist()[3:6] == [3,2,3])
    
    two_day_sum = df.rolling(MyStartOfDayIndexer(on=df.timestamp,offset='1d',closed='both')).sum()
    assert(two_day_sum['value'].tolist()[3:6] == [4,3,4])

if __name__=="__main__":
    test_my_indexer()
