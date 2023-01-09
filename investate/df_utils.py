from collections import defaultdict
import numpy as np


class divide_by_first:
    """
    Get the period growths for an investment whose values over time are given in a series
    """

    def __init__(self, date=None):
        self.date = date

    def fit_transform(self, series):
        """Get first term and divide all by first"""
        if self.date:
            divisor = series.loc[self.date]
        else:
            divisor = series.iloc[0]
        series.apply(lambda x: x / divisor)
        return series.apply(lambda x: x / divisor)


def normalize_df(df,
                 columns=None,
                 method=divide_by_first):
    """
    Normalize the columns of a dataframe
    """
    if columns is None:
        columns = df.columns
    scaler = method()
    df_norm = df.copy()
    for col in columns:
        # if the fit_transform works on a series
        try:
            df_norm[col] = scaler.fit_transform(df_norm[col])
        # otherwise, like standard scaler, turn everything into an array of array of single value
        except Exception as E:
            df_norm[col] = scaler.fit_transform(np.array(df_norm[col]).reshape(-1, 1))
    return df_norm


def get_dates_overlap(dfs, date_col_names='date'):
    if isinstance(date_col_names, str):
        date_col_names = [date_col_names] * len(dfs)
    else:
        assert len(dfs) == len(date_col_names), "You must provide a single common date" \
                                                " column name or a list of such name of same length as dfs"
    date_overlap = set(dfs[0][date_col_names[0]])
    for df, date_col_name in zip(dfs[1:], date_col_names[1:]):
        new_dates = set(df[date_col_name])
        date_overlap = date_overlap.intersection(new_dates)
    return date_overlap


def date_align_dfs(dfs, date_col_names='date'):
    """
    Return the sub-dfs of the dfs where only the common dates are kept. This is intended to use with dfs
    which have slightly different dates, typically holidays for one exchange that wasn't one for another
    """

    if isinstance(date_col_names, str):
        date_col_names = [date_col_names] * len(dfs)
    else:
        assert len(dfs) == len(date_col_names), "You must provide a single common date" \
                                                " column name or a list of such name of same length as dfs"
    dates_overlap = get_dates_overlap(dfs, date_col_names)
    date_aligned_dfs = []
    for df, date_col_name in zip(dfs, date_col_names):
        date_aligned_dfs.append(df[df[date_col_name].isin(dates_overlap)])
    return date_aligned_dfs


def add_weekday_to_df(df, data_col='date'):
    df['weekday'] = df[data_col].dt.day_name()
    return df


def add_day_to_df(df, data_col='date', extract_func=lambda x: str(x)[:10]):
    df['day'] = df[data_col].apply(extract_func)
    return df


def add_min_to_df(df, data_col='date', extract_func=lambda x: str(x)[11:16]):
    df['minute'] = df[data_col].apply(extract_func)
    return df


default_aggreg_func = lambda df: (df['close'].iloc[0] - df['open'].iloc[0]) / df['open'].iloc[0]


def get_stats_for_groupby(df,
                          group_by_cols=['day', ],
                          groupname_to_aggreg_type=lambda x: x[0],
                          aggreg_stats=default_aggreg_func):
    results = defaultdict(list)
    for groupname, group_df in df.groupby(group_by_cols):
        aggreg_type = groupname_to_aggreg_type(groupname)
        results[aggreg_type].append(aggreg_stats(group_df))
    return results


def aggreg_results(results_dict,
                   aggreg_func=lambda x: np.mean(x)):
    aggreg_res_dict = dict()
    for key, val in results_dict.items():
        aggreg_res_dict[key] = aggreg_func(val)
    return aggreg_res_dict

# Example to get mean growth for each day of the week for SPY, where spy_df is the
# df of the daily open/close value of SPY
# daily_growth = aggreg_results(get_stats_for_groupby(spy_df,
#                                                     group_by_cols=['weekday', 'day']))
