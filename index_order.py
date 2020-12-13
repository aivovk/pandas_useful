import pandas as pd

"""
a minimal example where the goal is to create 'new_column' which is the sum
of 'old_column' over the last 7 days for a particular 'group_name'
"""

df = pd.DataFrame([['A','2020-01-01',0],
                   ['B','2020-01-01',1],
                   ['A','2020-01-04',0],
                   ['B','2020-01-04',1]],
                  columns=['group_name','timestamp','old_column'])
df['timestamp'] = pd.to_datetime(df['timestamp'])
print(df)

# save column order (optional)
# any columns not explicitly added here will get dropped when df=df[col_order] is called
col_order = df.columns.tolist() + ['new_column']

# save row order
df.reset_index(inplace=True)

# need to use a multi-index to assign to our frame, since the 'timestamp' might
# not be unique
df.set_index(['group_name', 'timestamp'],inplace=True)

# rolling can either use a column or an index (not a multi-index), so put
# 'group_name' back into a column before doing groupby+rolling
df['new_column'] = df.reset_index(level=0).groupby('group_name').\
    rolling('7d',closed='both')['old_column'].sum()

# put the 'timestamp' and 'group_name' back into columns
df.reset_index(inplace=True)

# restore the row order
df.set_index('index', inplace=True)

# restore the column order (optional)
df = df[col_order]

print(df)
