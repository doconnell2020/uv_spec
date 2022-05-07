def clean_data(df):
    #Remove unnecessary lines
    df = df.copy().dropna().reset_index().drop(['index', 'User: USER', 'Unnamed: 1'], axis=1)
    df.columns = df.iloc[0]
    df = df.drop(0)
    #Cast all data to be float type for numerical operations
    df = df.astype('float')


def get_blank_data(df):
    df = df.tail(3)
    df = df.groupby(by='Dilution').mean()