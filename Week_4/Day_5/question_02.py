import pandas as pd
import sys
from supporting_files.data_loader import load_excel

df = load_excel('../supporting_files/SaleData.xlsx')


"""
Write a Pandas program to find the total sale amount (Sale_amt) region and manager wise. 
Order the dataframe by Sale_amt, starting with the highest.
Output should be DataFrame with 3 columns (order is important):
    - Region
    - Manager
    - Sale_amt
and numeric index starting with 0 (after sorting).
"""
ddf = pd.read_excel (r'supporting_files/SaleData.xlsx')


"""
Write a Pandas program to find the total sale amount (Sale_amt) region and manager wise. 
Order the dataframe by Sale_amt, starting with the highest.
Output should be DataFrame with 3 columns (order is important):
    - Region
    - Manager
    - Sale_amt
and numeric index starting with 0 (after sorting).
"""
def compute_total_sale(df):
    df2 = pd.DataFrame(df.groupby(['Region','Manager']).sum()['Sale_amt'].sort_values(ascending=False))
    df2.reset_index(level=1, inplace=True)
    df2.reset_index(level=0, inplace=True)
    return df2