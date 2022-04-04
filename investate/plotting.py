"""
A few useful functions to plot financial features
"""
import matplotlib.pyplot as plt


def color_according_to_monotonicity(
    series, col_up='g', col_down='r', color_equal='g', start_col='g'
):
    """Makes a series of strings of matplotlib colors depending on the monotonicity of

     >>> series = [1, 2, 3, 2, 3, 3]
     >>> color_according_to_monotonicity(series, col_up='u', col_down='d', color_equal='e', start_col='s')
     ['s', 'u', 'u', 'd', 'u', 'e']
    """

    colors = [start_col]
    first = series[0]
    for second in series[1:]:
        if second < first:
            col = col_down
        elif second > first:
            col = col_up
        else:
            col = color_equal
        colors.append(col)
        first = second
    return colors


def sparsify_and_rotate_ticks(ax, rotation=90, one_tick_every=4):
    ticks = ax.get_xticks()
    ax.set_xticklabels(ticks, rotation=rotation)
    for n, label in enumerate(ax.xaxis.get_ticklabels()):
        if n % one_tick_every != 0:
            label.set_visible(False)


def plot_series(
    series,
    col_func=color_according_to_monotonicity,
    plot_kwargs={'kind': 'bar'},
    ax_func=sparsify_and_rotate_ticks,
):
    my_colors = col_func(series)
    ax = series.plot(**plot_kwargs, color=my_colors)
    ax_func(ax)
    return ax


def plot_lines(
    ax,
    lines_loc,
    label=None,
    color='r',
    line_width=0.5,
    line_style='-',
    line_type='vert',
    alpha=1,
):
    """
    Function to draw vertical or horizontal lines on an ax
    :param ax: the matplolib axis on which to draw
    :param lines_loc: the location of the lines
    :param labels: a list of floats, the labels of the lines, optionsl
    :param colors: a list of strings, the colors of the lines
    :param line_widths: a list of floats, the widths of the lines
    :param def_col: default color if no list of colors if provided
    :param line_type: 'vert' or 'horiz
    :return:

    --------------EXAMPLE OF USAGE---------------

    # an initial plot
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3])

    # adding vertical lines to the plot
    plot_vlines(ax,
                lines_loc=[1,2],
                line_type='horiz',
                colors=['b', 'r'],
                line_widths=[0.5, 2],
                labels=['thin blue', 'wide red'])
    """

    if line_type == 'vert':
        line_ = ax.axvline
    if line_type == 'horiz':
        line_ = ax.axhline
    for line in lines_loc:
        line_(
            line,
            c=color,
            linewidth=line_width,
            label=label,
            linestyle=line_style,
            alpha=alpha,
        )
        # only the first one produce a label
        label = None

    return ax
