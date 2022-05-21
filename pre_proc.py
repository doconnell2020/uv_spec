
def restructure_data(df):
    #Remove unnecessary lines
    df = df.copy().dropna().reset_index().drop(['index', 'User: USER', 'Unnamed: 1'], axis=1)
    df.columns = df.iloc[0]
    df = df.drop(0)
    #Cast all data to be float type for numerical operations
    return df.astype('float')
    

def blank_data(df):
    df = restructure_data(df)
    #Blanks are teh final three rows
    blanks = df.tail(3)
    return blanks.groupby(by='Dilution').mean()
    

def simple_samples(df):
    df = restructure_data(df)
    #The samples are all rows until the last 3, which are blanks
    samples = df.iloc[:-3]
    return samples.groupby(by='Dilution').mean()


def norm_samples(df):
    return simple_samples(df).subtract(blank_data(df).values.squeeze())
