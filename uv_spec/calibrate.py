'''Calibrate the model before passing the test data to "find_conc.py"'''

import pandas as pd 
import sys 

filename = sys.argv[1]

master_df = pd.read_csv(str(filename))

def clean_data(df):
    #Remove unnecessary lines
    df = df.copy().dropna().reset_index().drop(['index', 'User: USER', 'Unnamed: 1'], axis=1)
    df.columns = df.iloc[0]
    df = df.drop(0)
    #Cast all data to be float type for numerical operations
    df = df.astype('float')


