import matplotlib.pyplot as plt
def main(df):
    """Testing the distplot function"""
    fig, ax = plt.subplots()
    df.distplot('mpg', ax=ax)
    fig.savefig('./mltools/tests/plots/distplot.png')
    return 1