def main(df):
    """Testing the log function"""
    return list(df.drop(['car name'], axis=1).log(
                   columns='mpg', verbose=True)['mpg'].iloc[0:20])