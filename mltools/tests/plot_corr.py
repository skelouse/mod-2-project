def main(df):
    """Testing the qq_plot function"""
    df.clean_col_names(inplace=True, verbose=False)
    df.drop('car_name', axis=1, inplace=True)
    df.lrmodel('mpg', inplace=True, verbose=False)
    fig, ax = df.plot_corr(annot=True)
    fig.savefig('./mltools/tests/plots/corr.png')
    return 1