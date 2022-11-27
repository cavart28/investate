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


def normalize_df(df, columns=None, method=divide_by_first):
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
