# add verbose argument to print more information on some functions
# figure out wraps
# do examples in the doc strings

#possibly use cook's distance outlier removal  (YellowBrick package - Slack from James)

import copy
import inspect
import pandas as pd
import numpy as np
from functools import wraps, partial
import statsmodels.api as sm
import statsmodels.formula.api as smf
import scipy.stats as stats
import statsmodels.stats.api as sms
from statsmodels.stats.outliers_influence import variance_inflation_factor
from functools import wraps
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import seaborn as sns
import missingno as ms


from inspect import getmembers, isfunction
"https://stackoverflow.com/questions/17393176/python-3-method-docstring-inheritance-without-breaking-decorators-or-violating"
def inherit_docstrings(cls):
    for name, func in getmembers(cls, isfunction):
        if func.__doc__: continue
        for parent in cls.__mro__[1:]:
            if hasattr(parent, name):
                func.__doc__ = getattr(parent, name).__doc__
    return cls


class MLFrame(pd.DataFrame):
    """A pd.DataFrame with an inplace model, and LinearRegression
    modeling functions.
    
    **See pandas.DataFrame documentation"""
    model = None

    def __init__(self, frame, **kwargs):
        super(MLFrame, self).__init__(frame, **kwargs)

    def cat_cols(self):
        """Computes and returns Categorical columns"""
        return list(self.select_dtypes('object').columns)

    def num_cols(self):
        """Computes and returns Numerical columns"""
        return list(self.select_dtypes('number').columns)

    @staticmethod
    def replace_all(string):
        """Replaces bad characters in a string for
        column names to work in a R~formula"""
        return string.replace(
                      ' ', '_').replace(
                      '(', '').replace(
                      ')', '').replace(
                    #   '1', 'one').replace(
                    #   '2', 'two').replace(
                    #   '3', 'three').replace(
                    #   '4', 'four').replace(
                    #   '5', 'five').replace(
                    #   '6', 'six').replace(
                    #   '7', 'seven').replace(
                    #   '8', 'eight').replace(
                    #   '9', 'nine').replace(
                      '.', '_').replace(
                      '-', '_').replace(
                      '/', '_').replace(
                      '@', '_').replace(
                      '+', '_').replace(
                      ' ', '_').replace(
                      ' ', '_')

    def clean_col_names(self,
                        inplace=False,
                        verbose=True):
        """Cleans the column names of a DataFrame
        for use in an R~Formula

        Parameters
        ----------------------------------------
        inplace[bool]::
            Defines whether to return a new dataframe or
            mutate the dataframe
        verbose[bool]::
            Whether to show the difference between
            the old columns and clean columns or not

        Returns
        ----------------------------------------
        None if inplace, otherwise returns a copy of the dataframe

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.clean_col_names()
        Columns changed:
        model year --> model_year
        car name --> car_name
        """
        def show_difference(old_cols, new_cols):
            diff = dict(zip(old_cols, new_cols))
            print('\nColumns changed:')
            for col in diff.items():
                if col[0] != col[1]:
                    print(col[0], "-->", col[1])

        if inplace:
            new_columns = [self.replace_all(c.strip())
                            for c in self.columns.values.tolist()]
            old_columns = self.columns
            if verbose:
                show_difference(old_columns, new_columns)
            self.columns = new_columns
        else:
            df = self.copy()
            new_columns = [self.replace_all(c.strip())
                            for c in df.columns.values.tolist()]
            old_columns = df.columns
            if verbose:
                show_difference(old_columns, new_columns)
            df.columns = new_columns
            return df

    def get_vif(self, target, verbose=True):
        """Computes the Variance Inflation Factor
        for the columns of a dataframe based
        on the target column

        Parameters
        ----------------------------------------
        target[str]::
            The column name to base the VIF on
        verbose[bool]::
            Whether or not to print out the VIF series

        Returns
        ----------------------------------------
        Series of variance_inflation_factor for each column

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.drop(['car name'], axis=1, inplace=True)
        >>> df.get_vif('mpg', verbose=False)
        const          763.558
        cylinders       10.738
        displacement    21.837
        horsepower       9.944
        weight          10.831
        acceleration     2.626
        model year       1.245
        origin           1.772
        """
        X = self.drop(target, axis=1)
        X= sm.add_constant(X)
        vif = [variance_inflation_factor(X.values, i)
            for i in range(X.shape[1])]
        s = pd.Series(dict(zip(X.columns, vif)))
        if verbose:
            print(s)
        return s

    def get_vif_cols(self, target, threshold=6, verbose=True):
        """ Computes Variance Inflation Factor
        for the dataframe, and gets the columns
        that are above the defined threshold

        Parameters
        ----------------------------------------
        target[str]::
            The column name to base the VIF on
        threshold=6[int]::
            The threshold that columns would be above
            where they are an issue, and need to be
            looked at
        verbose[bool]::
            Whether to print out the series or not

        Returns
        ----------------------------------------
        Series of variance_inflation_factor for each column

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.drop(['car name'], axis=1, inplace=True)
        >>> df.get_vif_cols('mpg', verbose=False)
        horsepower      9.944
        cylinders      10.738
        weight         10.831
        displacement   21.837
        dtype: float64
        """
        vif_results = self.get_vif(target, verbose=False)
        bad_vif = list(vif_results[vif_results>threshold].index)
        if 'const' in bad_vif:
            bad_vif.remove('const')
        num_vif = {}
        for col in bad_vif:
            num_vif[col] = vif_results[col]
        s = pd.Series(num_vif).sort_values()
        if verbose:
            print('\nVIF columns > %s'%threshold, s)
        return s

    def log(self, columns, inplace=False, verbose=True):
        """ logs the listed columns of the dataframe
        Parameters
        ----------------------------------------
        columns[list, str]::
            A list of columns to make logarithmic
        inplace[bool]::
            Defines whether to return a new dataframe or
            mutate the dataframe
        verbose[bool]::
            Whether to print out logged columns or not

        Returns
        ----------------------------------------
        None if inplace otherwise returns a copy
        of the dataframe with columns logged

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.drop(['car name'], axis=1, inplace = True)
        
        >>> df = df.log(columns=['mpg', 'cylinders'])
        Logging:
           mpg
           cylinders
        # OR
        >>> df.log('mpg', inplace=True)
        Logging:
           mpg
        """
        if verbose:
            print("Logging:")
            if isinstance(columns, list):
                for col in columns:
                    print("  ", col)
            else:
                print("  ", columns)
        if inplace:
            if isinstance(columns, list):
                for col in columns:
                    self[col] = np.log(self[col])
            else:
                self[columns] = np.log(self[columns])
        else:
            df = self.copy()
            if isinstance(columns, list):
                for col in columns:
                    df[col] = np.log(df[col])
            else:
                df[columns] = np.log(df[columns])
            return df

    def scale(self, columns, inplace=False, verbose=True):
        """ Scales the listed columns of the dataframe
        Parameters
        ----------------------------------------
        columns[list, str]::
            A list of columns to scale
        inplace[bool]::
            Defines whether to return a new dataframe or
            mutate the dataframe
        verbose[bool]::
            Whether to print out the scaled columns or not

        Returns:
            None if inplace otherwise returns a copy
            of the dataframe with columns scaled

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.drop(['car name'], axis=1, inplace = True)
        
        >>> df = df.scale(columns=['mpg', 'cylinders'])
        Scaling:
           mpg
           cylinders
        # OR
        >>> df.scale('mpg', inplace=True)
        Scaling:
           mpg
        """
        def scale(df, col):
            df[col] = ((df[col] - np.mean(df[col]))
                      / np.sqrt(np.var(df[col])))
        if verbose:
            print("Logging:")
            if isinstance(columns, list):
                for col in columns:
                    print("  ", col)
            else:
                print("  ", columns)
        if inplace:
            if isinstance(columns, list):
                for col in columns:
                    scale(self, col)
            else:
                scale(self, columns)
        else:
            df = self.copy()
            if isinstance(columns, list):
                for col in columns:
                    scale(df, col)
            else:
                scale(df, columns)
            return df

    def wrapper(func):
        """Wrapper to return a MLFrame, and set
        the model when defined pd.DataFrame methods
        are used on a MLFrame"""
        @wraps(func)
        @inherit_docstrings
        def inner(self, *args, **kwargs):
            frame = func(self, *args, **kwargs)
            frame = MLFrame(frame)
            frame.model = self.model
            return frame
        return inner

    @wrapper
    def drop(self, *args, **kwargs):
        return super(MLFrame, self).drop(*args, **kwargs)

    @wrapper
    def copy(self, *args, **kwargs):
        return super(MLFrame, self).copy(*args, **kwargs)
    
    @wrapper
    def wrap__getitem__(self, df):
        return df

    def __getitem__(self, key):
        """Wrapper for get item [] so that it returns an
        MLFrame rather then a pd.DataFrame"""
        call = super().__getitem__(key)
        if isinstance(call, pd.DataFrame):
            return self.wrap__getitem__(call)
        else:
            return call

    def info(self, *args, **kwargs):
        print("Model is %s\n" % self.model)
        return super(MLFrame, self).info(*args, **kwargs)

    def one_hot_encode(self,
                        columns=[],
                        drop_first=True,
                        verbose=True,
                        **kwargs):
        """Makes a one hot encoded dataframe

        Parameters
        ----------------------------------------
        columns[list]::
            list of columns to one hot encode
            uses self.cat_cols() if not defined
        drop_first=True::
            whether to drop the first column or not
            to rid of multicollinearity
        verbose[bool]::
            Whether to print out the series or not
        kwargs{dict}::
            Arguments to send to pd.get_dummies
            see:
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.get_dummies.html

        Returns
        ----------------------------------------
        encoded dataframe

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.clean_col_names(verbose=False, inplace=True)
        >>> # splitting car_name into model for categorizing
        >>> df['model'] = df['car_name'].apply(
        >>>     lambda x: x.split(' ')[0])
        >>> df_ohe = df.one_hot_encode(columns=['model'])
        Added categorical columns
        37 -> model
        """
        if not isinstance(columns, list):
            raise(AttributeError('%s not a list' % columns))
        elif not columns:
            columns = self.cat_cols()
        df = MLFrame(pd.get_dummies(self,
                                    columns=columns,
                                    drop_first=drop_first,
                                    **kwargs))
        
        if verbose:
            print("Added categorical columns")
            count_dict = {}
            for col in self.columns:
                count = 0
                for col_ohe in df.columns:
                    if col in col_ohe:
                        count += 1
                if count > 1:
                    count_dict[col] = count
            for col, num in sorted(count_dict.items(), 
                    key=lambda x: x[1]):
                print(num, '->', col)
                                
        return df

    def find_outliers_IQR(self, col, verbose=True):
        """Finds outliers using the IQR method

        Parameters
        ----------------------------------------
        col[str]::
            Name of the column to search for outliers in
        verbose[bool]::
            Whether to print out the series or not

        Returns
        ----------------------------------------
        True/False Series of the outliers (True is outlier)

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> idx_outliers = df.find_outliers_IQR('horsepower', verbose=True)
        Found 10 outliers using IQR in horsepower or ~ 2.55%
        >>> df = MLFrame(df[~idx_outliers])
        """
        data = self[col]
        res = data.describe()
        IQR = res['75%']-res['25%']
        thresh = 1.5* IQR
        idx_outliers = ((data<res['25%']-thresh)
                         | (data > res['75%']+thresh))
        if verbose:
            total = idx_outliers.sum()
            total_perc = round((total/len(self))*100, 2)
            print("Found {} outliers using IQR in {} or ~ {}%"
                  .format(total, col, total_perc))
        return idx_outliers

    def find_outliers_Z(self, col, verbose=True):
        """Finds outliers using the z_score method
        ----------------------------------------
        col[str]::
            Name of the column to search for outliers in
        verbose[bool]::
            Whether to print out the series or not

        Returns
        ----------------------------------------
        True/False Series of the outliers (True is outlier)

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> idx_outliers = df.find_outliers_Z('horsepower', verbose=True)
        Found 5 outliers using IQR in horsepower or ~ 1.28%
        >>> df = MLFrame(df[~idx_outliers])
        """
        data = self[col]
        z_scores = np.abs(stats.zscore(data))
        z_scores = pd.Series(z_scores, index=data.index)
        idx_outliers =z_scores > 3
        if verbose:
            total = idx_outliers.sum()
            total_perc = round((total/len(self))*100, 2)
            print("Found {} outliers using IQR in {} or ~ {}%"
                  .format(total, col, total_perc))
        return idx_outliers    

    def outlier_removal(self,
                        columns=[],
                        IQR=False,
                        z_score=False,
                        verbose=True):
        """Removes outliers based on IQR or z_score

        Parameters
        ----------------------------------------
        column[list, str]::
            The columns of which to remove outliers
            if blank, removes from all columns
        IQR[bool]::
            Whether or not to remove outliers
            using IQR method
        z_score[bool]::
            Whether or not to remove outliers
            using z_score method
        verbose[bool]::
            Whether to print how many outliers were
            found in each column or now       

        Returns
        ----------------------------------------
        Copy of dataframe with outliers removed

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df = df.outlier_removal('horsepower',
        ...                          IQR=True)
        Found 10 outliers using IQR in horsepower or ~ 2.55%
        Removed
        >>> # OR
        >>> df = df.outlier_removal(['horsepower', 'mpg'], 
                                 z_score=True)
        Found 10 outliers using IQR in horsepower or ~ 2.55%
        Removed
        Found 0 outliers using IQR in mpg or ~ 0.0%
        Removed
        """
        if IQR:
            func = partial(self.find_outliers_IQR,
                           verbose=verbose)
        elif z_score:
            func = partial(self.find_outliers_Z,
                           verbose=verbose)

        df = self.copy()
        if isinstance(columns, list):
            if not columns:
                columns = self.columns
            for col in columns:
                outliers = func(col)
                num = len(df)
                df = df[~outliers]
                if verbose:
                    print('Removed')
        else:
            outliers = func(columns)
            df = df[~outliers]
            if verbose:
                print('Removed')
        return df

    def get_nulls(self, verbose=True):
        """Returns sum of all nulls in the dataframe

        Parameters
        ----------------------------------------
        verbose[bool]::
            Whether to print out the null count of
            each row or not

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.DataFrame(np.arange(12).reshape(3, 4),
        ...                   columns=['A', 'B', 'C', 'D']))
        >>> df['A'].loc[1:3] = np.nan
        >>> df['B'].loc[0] = np.nan
        >>> df
            A    B   C   D
        0  0.0  NaN   2   3
        1  NaN  5.0   6   7
        2  NaN  9.0  10  11
        >>> df.get_nulls(verbose=False)
        3
        """
        nulls = self.isna().sum()
        if verbose:
            print(nulls)
        nulls = nulls.sum()
        return nulls

    def drop_nulls_perc(self, perc,
                        inplace=False,
                        verbose=True):
        """Drops a column if the null value is over a
        certain percentage (0-1)

        Parameters
        ----------------------------------------
        perc::[float]
            The percentage under which nulls are for a column
            to get dropped
        inplace[bool]::
            Defines whether to return a new dataframe or
            mutate the dataframe
        verbose[bool]::
            Whether to print out the series or not

        Returns
        ----------------------------------------
        None if inplace, otherwise returns copy of dataframe
        with columns dropped

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.DataFrame(np.arange(12).reshape(3, 4),
        ...                   columns=['A', 'B', 'C', 'D']))
        >>> df['A'].loc[1:3] = np.nan
        >>> df['B'].loc[0] = np.nan
        >>> df
            A    B   C   D
        0  0.0  NaN   2   3
        1  NaN  5.0   6   7
        2  NaN  9.0  10  11
        >>> df.drop_nulls_perc(.4)
            B   C   D
        0  NaN   2   3
        1  5.0   6   7
        2  9.0  10  11
        """
        nulls = self.isna().sum()
        drop_cols = nulls[nulls/len(self) > perc].index
        if verbose:
            print('Dropping: ')
            for col in drop_cols:
                print('    --> ', col)
        return self.drop(columns=drop_cols, inplace=inplace)

    def ms_matrix(self, **kwargs):
        """Plots a missingno matrix

        Parameters
        ----------------------------------------
        kwargs{dict}::
            Arguments to send to ms.matrix
        
        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.ms_matrix()

        """
        return ms.matrix(self, **kwargs)

    def fill_na_mode(self, inplace=False, verbose=True):
        """Fills na cells with the mode of it's
        respective column

        Parameters
        ----------------------------------------
        inplace[bool]::
            Defines whether to return a new dataframe or
            mutate the dataframe.
        verbose[bool]::
            Whether to print out the filling information
            or not.

        Returns
        ----------------------------------------
        None if inplace, otherwise returns copy of dataframe
        with nulls filled with mode

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.DataFrame(np.arange(12).reshape(3, 4),
        ...                   columns=['A', 'B', 'C', 'D']))
        >>> df['A'].loc[1:3] = np.nan
        >>> df['B'].loc[0] = np.nan
        >>> df
            A    B   C   D
        0  0.0  NaN   2   3
        1  NaN  5.0   6   7
        2  NaN  9.0  10  11
        >>> df.fill_na_mode()
        Filling 66.67% of A with nan
        Filling 33.33% of B with 9.0
            A    B    C   D
        0  0.0  5.0   2   3
        1  0.0  5.0   6   7
        2  0.0  9.0  10  11

        """
        nulls = self.isna().sum()
        null_perc = nulls[nulls>0]/len(self)
        null_cols = list(null_perc.index)
        null_modes = dict(self[null_cols].mode())
        if verbose:
            for col, perc in null_perc.items():
                print("Filling %s" % (round(perc*100, 2)),
                      "\b%", "of %s with %s"
                    % (col, null_modes[col]))
        if inplace:
            for col, mode in null_modes.items():
                self[col] = self[col].fillna(mode[0])
        else:
            df = self.copy()
            for col, mode in null_modes.items():
                df[col] = df[col].fillna(mode[0])
            return df

    def fill_na_mean(self, inplace=False, verbose=True):
        """Fills na cells with the mean of it's
        respective column

        Parameters
        ----------------------------------------
        inplace[bool]::
            Defines whether to return a new dataframe or
            mutate the dataframe.
        verbose[bool]::
            Whether to print out the filling information
            or not.

        Returns
        ----------------------------------------
        None if inplace, otherwise returns copy of dataframe
        with nulls filled with mean

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.DataFrame(np.arange(12).reshape(3, 4),
        ...                   columns=['A', 'B', 'C', 'D']))
        >>> df['A'].loc[1:3] = np.nan
        >>> df['B'].loc[0] = np.nan
        >>> df
            A    B   C   D
        0  0.0  NaN   2   3
        1  NaN  5.0   6   7
        2  NaN  9.0  10  11
        >>> df.fill_na_mean()
        Filling 66.67% of A with nan
        Filling 33.33% of B with 9.0
            A    B    C   D
        0  0.0  7.0   2   3
        1  0.0  5.0   6   7
        2  0.0  9.0  10  11

        """
        nulls = self.isna().sum()
        null_perc = nulls[nulls>0]/len(self)
        null_cols = list(null_perc.index)
        null_means = dict(self[null_cols].mean())
        if verbose:
            for col, perc in null_perc.items():
                print("Filling %s" % (round(perc*100, 2)),
                      "\b%", "of %s with %s"
                    % (col, null_means[col]))
        if inplace:
            for col, mean in null_means.items():
                self[col] = self[col].fillna(mean)
        else:
            df = self.copy()
            for col, mean in null_means.items():
                df[col] = df[col].fillna(mean)
            return df

    def fill_na_perc(self, inplace=False, verbose=True):
        """
        * Not implemented *
        Fills na cells with the percent value_counts
        of it's respective column

        Parameters
        ----------------------------------------
        inplace[bool]::
            Defines whether to return a new dataframe or
            mutate the dataframe
        verbose[bool]::
            Whether to print out how many were filled
            in each column or not

        Returns
        ----------------------------------------
        None if inplace, otherwise returns copy of dataframe
        with nulls filled with mode

        Example Usage
        ----------------------------------------
        """
        raise AttributeError('Not Implemented')

    def qq_plot(self, **kwargs):
        """Plots a statsmodels QQplot of the dataframe

        Parameters
        ----------------------------------------
        kwargs{dict}::
            Arguments to send to sm.graphics.qqplot()
            see:
        https://www.statsmodels.org/stable/generated/statsmodels.graphics.gofplots.qqplot.html

        Returns
        ----------------------------------------
        sm.graphics.qqplot()

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.clean_col_names(inplace=True)
        >>> df.lrmodel('mpg', inplace=True)
        >>> df.qq_plot()
        """
        if self.model:
            return sm.graphics.qqplot(self.model.resid,
                        fit=True, line='45', **kwargs)
        else:
            raise AttributeError('No model defined')

    def model_resid_scatter(self, target, ax=None,
                            scatter_kws={}, line_kws={}):
        """Plots a scatter plot and axhline 
        based on target and the model's residuals

        Parameters
        ----------------------------------------
        target[str]::
            The target of the model
        ax[matplotlib.axes]:
            The axis to plot onto
        scatter_kws{dict}::
            Arguments to send to the scatter plot
            see:
        https://matplotlib.org/3.3.1/api/_as_gen/matplotlib.pyplot.scatter.html
        line_kws{dict}::
            Arguments to send to the axhline
            see:
        https://matplotlib.org/3.3.1/api/_as_gen/matplotlib.pyplot.axhline.html

        Returns
        ----------------------------------------
        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.clean_col_names(inplace=True)
        >>> df.lrmodel('mpg', inplace=True)
        >>> df.model_resid_scatter('mpg')
        """
        if ax:
            ax.scatter(x=self[target],
                       y=self.model.resid,
                       **scatter_kws)
            ax.axhline(0, **line_kws)
            ax.set_xlabel(target)
            ax.set_ylabel('Model Residuals')
        else:
            plt.scatter(self[target],
                        self.model.resid,
                        **scatter_kws)
            plt.axhline(0, **line_kws)
            plt.xlabel(target)
            plt.ylabel('Model Residuals')
            plt.show()

    def lrmodel(self,
                 target=None,
                 columns=[],
                 inplace=False,
                 verbose=True,
                 **kwargs):
        """Creates a LinearRegression model of target

        Parameters
        ----------------------------------------
        target::[str]
            The target for which to model on
        cols[list]::
            a list of columns of which to build the model
            on.  If empty, uses all columns-target
        inplace[bool]::
            Defines whether to return a new dataframe or
            mutate the dataframe
        verbose[bool]::
            Whether or not to display the model.summary()
        kwargs{dict}::
            Arguments that are sent to Model.from_formula()
            see:
        https://www.statsmodels.org/stable/generated/statsmodels.formula.api.ols.html

        Returns
        ----------------------------------------
        None if inplace, otherwise returns the model

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.clean_col_names(inplace=True)
        >>> df.lrmodel('mpg', verbose=False, inplace=True)
        >>> df.model.pvalues.max()
        0.9996627853521083
        """
        if not target:
            raise AttributeError('No target defined')
        if not columns:
            columns = self.drop(target, axis=1).columns
        cols_form = '+'.join(columns)
        # cols_form = cols_form.replace(' ', '')
        formula='%s~%s' % (target, cols_form)
        # possibly svd did not converge here
        kwds = dict(formula=formula, data=self)
        kwds.update(**kwargs)
        model = smf.ols(**kwds).fit()
        try:  # undefined if used outside jupyter
            if verbose:
                display(model.summary())
        except NameError:
            print(model.summary())
        
        if inplace:
            self.model = model
        else:
            return model

    def model_and_plot(self,
                      target,
                      figsize=(10, 10),
                      **kwargs):
        """Creates a new model based on target, plots a
        scatter plot of (target, model residuals), and
        plots a qqplot based on the model residuals.

        Parameters
        ----------------------------------------
        target::[str]
            The target for which to model on
        kwargs{dict}::
            Arguments that are sent to Model.from_formula()
            see:
        https://www.statsmodels.org/stable/generated/statsmodels.formula.api.ols.html

        Returns
        ----------------------------------------
        model

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.clean_col_names(inplace=True)
        >>> df.model_and_plot('mpg')
        """
        self.lrmodel(target=target, inplace=True, verbose=True)
        model = self.model
        fig, axes = plt.subplots(nrows=2, figsize=figsize)
        fig.tight_layout(pad=8.0)
        self.qq_plot(ax=axes[0])
        self.model_resid_scatter(target, ax=axes[1],
            line_kws=dict(color='k'))
        return model
        

    def plot_corr(self, figsize=(25, 25), annot=False,
                  **kwargs):
        """Plots a predefined correlation heatmap

        Parameters
        ----------------------------------------
        figsize(tu, ple)::
            The size of the plotted figure
        annot[bool]::
            Whether or not to annotate the cells
        kwargs{dict}::
            Arguments that are sent to sns.heatmap
            see:
        https://seaborn.pydata.org/generated/seaborn.heatmap.html

        Returns
        ----------------------------------------
        fig, ax
        
        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.clean_col_names(inplace=True, verbose=False)
        >>> df.drop('car_name', axis=1, inplace=True)
        >>> df.plot_corr(annot=True)
        """
        corr=np.abs(self.corr())
        fig, ax = plt.subplots(figsize=figsize)
        mask=np.zeros_like(corr, dtype=np.bool)
        mask[np.triu_indices_from(mask, k=0)] = True
        kwds = dict(mask=mask,
                    cmap=sns.diverging_palette(240, 10, n=10),
                    annot=annot,
                    center=0,
                    ax=ax,
                    linewidths=1,
                    square=True,
                    cbar_kws={'shrink':0.6})
        kwds.update(**kwargs)
        sns.heatmap(corr, **kwds)
        return fig, ax

    def plot_coef(self, cmap='Greens'):
        """Plots a predefined plot
        of the model's coefficients

        cmap[str]:: Default is Greens
            The style.background_gradient color
            see:
        https://matplotlib.org/3.3.1/tutorials/colors/colormaps.html

        Returns
        ----------------------------------------
        <pandas.io.formats.style.Styler>
        
        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.clean_col_names(inplace=True, verbose=False)
        >>> df.drop('car_name', axis=1, inplace=True)
        >>> df.plot_corr(annot=True)
        """
        coeffs = self.model.params.sort_values(ascending=False)
        frame = coeffs.to_frame('Coefficients')
        styler = frame.style.background_gradient(cmap=cmap)
        return styler

    def regplot(self, x, y, **kwargs):
        """Plots a seaborn regplot of x and y

        Parameters
        ----------------------------------------
        x[str]::
            Name of a column to plot x
        y[str]::
            Name of a column to plot y
        kwargs{dict}::
            Arguments that are sent to sns.regplot
            see:
        https://seaborn.pydata.org/generated/seaborn.regplot.html

        Returns
        ----------------------------------------
        an sns.regplot

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> fig, ax = plt.subplots()
        >>> df.regplot('horsepower', 'mpg', ax=ax)
        """
        return sns.regplot(x, y, data=self, **kwargs)

    def distplot(self, target, **kwargs):
        """Plots a seaborn displot of target
        Parameters
        ----------------------------------------
        target[str]::
            Name of the column of which to plot
        kwargs{dict}::
            Arguments to send in with sns.distplot()
            see:
        https://seaborn.pydata.org/generated/seaborn.distplot.html
            
        
        Returns
        ----------------------------------------
        an sns.distplot

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> fig, ax = plt.subplots()
        >>> df.distplot('mpg', ax=ax)
        """
        return sns.distplot(self[target], **kwargs)

    def jointplot(self, x, target, **kwargs):
        """Plots a seaborn jointplot of x and target
        Parameters
        ----------------------------------------
        x[str]::
            Name of a column to plot x
        target[str]::
            Name of the column of which to target
        kwargs{dict}::
            Arguments to send in with sns.jointplot()
            see:
        https://seaborn.pydata.org/generated/seaborn.jointplot.html
        
        Returns
        ----------------------------------------
        an sns.jointplot

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.jointplot('horsepower', 'mpg')
        """
        return sns.jointplot(data=self, x=x, y=target, **kwargs)

    def boxplot(self, target, **kwargs):
        """Plots a seaborn boxplot of target
        Parameters
        ----------------------------------------
        target[str]::
            Name of the column of which to plot
        kwargs{dict}::
            Arguments to send in with sns.boxplot()
            see:
        https://seaborn.pydata.org/generated/seaborn.boxplot.html
        
        Returns
        ----------------------------------------
        an sns.boxplot

        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> fig, ax = plt.subplots()
        >>> df.boxplot('mpg', ax=ax)
        """
        return sns.boxplot(y=self[target], **kwargs)

    def train_test_split(self,
                         target,
                         test_size=100,
                         seed=42,
                         verbose=True):
        """
        Parameters
        ----------------------------------------
        target[str]::
            Name of the column of which to target
        test_size[int]::
            How many times to run the train_test_split
        seed[int]::
            The random seed to use
        verbose[bool]::
            Whether or not to show the model and plots
        
        Returns
        ----------------------------------------
        model[sm.regression.linear_model.RegressionResultsWrapper]::
            The best model of the train_test_split
        
        Example Usage
        ----------------------------------------
        >>> df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
        >>> df.clean_col_names(inplace=True)
        >>> df.drop(['car_name', 'origin'], axis=1, inplace=True)
        >>> model = df.train_test_split('mpg',
                                        test_size=5,
                                        verbose=False)
        >>> model.pvalues
        Intercept      0.005
        cylinders      0.503
        displacement   0.688
        horsepower     0.868
        weight         0.000
        acceleration   0.510
        model_year     0.000
        dtype: float64
        """
        r2dict = {}
        r2scores = {}
        test_amount = test_size
        for x in range(0, test_amount):
            np.random.seed(seed)
            choices = [.3, .2, .1, .05]
            c = np.random.choice(choices)
            # X = self.drop(target, axis=1).copy()
            # y = self[target].copy()
            df_train, df_test = train_test_split(
                                    self,
                                    test_size=c,
                                    random_state=seed)
            df_train = MLFrame(df_train)
            df_test = MLFrame(df_test)

            model = df_train.lrmodel(target, verbose=False)
            r2dict.update({model.rsquared:(
                model, df_train[target], c)})
            y_train = model.predict(df_train)
            y_test = model.predict(df_test)
            r2_train = r2_score(df_train[target],y_train)
            r2_test = r2_score(df_test[target],y_test)
        model, X, test_size = sorted(r2dict.items(),
                                  key=lambda x: x[0])[-1][1]
        
        self.model = model
        fig, axes = plt.subplots(nrows=2, figsize=(10, 10))
        fig.tight_layout(pad=8.0)
        self.qq_plot(ax=axes[0])
        axes[1].scatter(X, self.model.resid)
        axes[1].axhline(0, color='k')
        axes[1].set_xlabel(target)
        axes[1].set_ylabel('Model Residuals')
        if verbose:
            print('test_size = ', test_size)
            try:
                display(model.summary())
            except NameError:
                print(model.summary())
            plt.show()
        return model


def test_car():
    df = MLFrame(pd.read_csv('mltools/tests/auto-mpg.csv'))
    df.clean_col_names(inplace=True)
    df['model'] = df['car_name'].apply(lambda x: x.split(' ')[0])
    df.drop(['car_name'], axis=1, inplace=True)
    df['model'] = df['model'].astype('category')
    df_ohe = df.one_hot_encode(['model'])
    df_ohe.clean_col_names(inplace=True)
    df_ohe.model_and_plot('horsepower', inplace=True)
    print(df_ohe.model.summary())

def test_houses():
    df = MLFrame(pd.read_csv('kc_house_data.csv'))
    first_model = df.fill_na_mode(  # Fill na for the model
        ).drop(['date', 'sqft_basement'], axis=1  # Dropping date and
        ).model_and_plot('price')                 # sqft_basement for example
    #df.model = first_model
    #df.plot_coef()
    #df.plot_corr(annot=True)
    df['sqft_basement'] = df['sqft_basement'].apply(
        lambda x: 0 if x == '?' else x)
    df['sqft_basement'] = df['sqft_basement'].astype(float)
    cat_cols = ['zipcode', 'condition', 'view']
    for col in cat_cols:
        df[col] = df[col].astype('category')
    df_ohe = df.drop(['date', 'id', 'lat', 'long'], axis=1
        ).one_hot_encode(cat_cols)
    df_ohe['waterfront'].fillna(0, inplace=True)
    df_ohe.fill_na_mode(inplace=True)
    drop_cols = [x for x in df_ohe.columns if 'condition' in x]
    drop_cols.append('sqft_living')
    df_ohe.drop(drop_cols, axis=1, inplace=True)
    df_ohe.clean_col_names(inplace=True)
    df_ohe.model_and_plot('price')
    print(df_ohe.model.summary())


if __name__ == "__main__":
    test_houses()
    
