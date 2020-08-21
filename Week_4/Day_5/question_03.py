import pandas as pd
import sys
from supporting_files.data_loader import load_excel

df = load_excel('supporting_files/SaleData.xlsx')


"""
Write a function to count the manager wise sale (sale_cnt)
and mean value of sale amount (sale_mean). 
Order the output dataframe by sale_cnt, starting with the highest.
Output should be DataFrame with 3 columns (order is important):
    - Manager
    - sale_cnt
    - sale_mean
and numeric index starting with 0 (after sorting).
"""

def compute_agg_stats(df):
    df2 = pd.DataFrame(df.groupby('Manager').sum()['Sale_amt'])
    df2.reset_index(level=0,inplace=True)
    df3 = pd.DataFrame(df['Manager'].value_counts())
    df3.reset_index(level=0,inplace=True)
    df3.rename(columns={'Manager':'sale_cnt','index':'Manager'},inplace=True)
    df4 = df3.merge(df2,on='Manager')
    df4['Sale_amt'] = df4['Sale_amt']/df4['sale_cnt']
    df4.sort_values(by='Sale_amt',ascending=False,inplace=True)
    return df4