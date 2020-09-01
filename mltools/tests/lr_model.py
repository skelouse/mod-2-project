def main(df):
    """Testing the lr_model function"""
    df.clean_col_names(inplace=True)
    return df.lrmodel(
        target='mpg',
        cols=df.columns)