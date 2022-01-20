from investate.series_utils import parallel_sort
from investate.moving_average import moving_stats


def get_comp_ma(
        series,
        chunk_sizes=(2, 4, 5),
        chk_funcs=[lambda x: x] * 3,
        pad_with=np.nan
):
    """
    Convenience function to compute and align several moving averages of a series
    """

    sorted_chunks, sorted_funcs = parallel_sort([chunk_sizes, chk_funcs])
    largest_chunks = sorted_chunks[-1]
    n_chunks = len(series) - largest_chunks + 1

    series = list(series)
    series.reverse()

    all_stats_series = []

    for chk_size, chk_func in zip(sorted_chunks, sorted_funcs):
        stat_series = []
        for i in range(n_chunks):
            chunk = series[i: i + chk_size]
            stat_series.append(chk_func(chunk))
        stat_series.reverse()
        all_stats_series.append(stat_series)
    series.reverse()

    if pad_with is not None:
        all_stats_series = [[pad_with] * (largest_chunks - 1) + i for i in all_stats_series]

    return all_stats_series


get_comp_ma(series=np.random.random(20),
            chunk_sizes=(2, 4, 15),
            chk_funcs=[np.mean] * 3,
            )