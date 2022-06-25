import os
from modelling_utils import Scale


def getParent(path, levels=0):
    """_summary_
    Get the parent directory of a path
    according to the specified level of
    depth in the tree
    Args:
        path    (str)   : child path of the parent directory
        levels  (int)   : number of levels to go up in the tree
    """
    common = path
    for _ in range(levels + 1):
        common = os.path.dirname(os.path.abspath(common))
    return common


def plotPrettyFFT(
    freq,
    power,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    file_path: str = None,
    xlog: bool = False,
    show: bool = False,
    target_harmonics: list = None,
    plot_to_terminal: bool = False,
    xscale: str = "",
    yscale: str = "",
    xunit: str = "Hz",
    yunit: str = "dB",
):
    """_summary_
    Plot a pretty FFT plot
    Args:
        freq (array/list): frequency array
        power (array/list): power array
        title (str)     : title of the plot
        xlabel (str)    : x-axis label
        ylabel (str)    : y-axis label
        file_path (str) : path to save the plot
        xlog (bool)     : log scale
        show (bool)     : show the plot
        target_harmonics (list): list (frequency, power) tuples of target harmonics to highlight
        xscale (str)    : x-axis scale
        yscale (str)    : y-axis scale
        xunit (str)     : x-axis unit. Default is Hz (hertz)
        yunit (str)     : y-axis unit. Default is dB (decibel)
    NOTE:
        kwargs example:
        kwargs = {
            "linefmt":"b-",
            "markerfmt":"bD",
            "basefmt":"r-",
        }
    """
    from loguru import logger as log
    import plotext as tplt
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    from numpy import min, where, max, floor, abs, array, append, sort, argsort
    import pdb
    from itertools import cycle

    plt.rc("axes", titlesize=14)  # fontsize of the axes title
    plt.rc("axes", labelsize=12)  # fontsize of the x and y labels
    plt.rc("xtick", labelsize=12)  # fontsize of the tick labels
    plt.rc("ytick", labelsize=12)  # fontsize of the tick labels
    plt.rc("legend", fontsize=11)  # legend fontsize
    plt.rc("font", size=11)  # controls default text sizes
    # define font family to use for all text
    rcParams["font.family"] = "serif"
    # plt.figure(figsize=(8,6))
    # markerline, stemlines, baseline = plt.stem(freq, power, bottom=min(power), use_line_collection=True, linefmt="b-", markerfmt="bD", basefmt="r-")
    # markerline.set_markerfacecolor("none")
    # stemlines.set_color("black")
    x_scale = 1.0
    if xscale != "":
        letter_scales = [letter for (letter, _) in [elem.value for elem in Scale]]
        value_scales = [value for (_, value) in [elem.value for elem in Scale]]
        if xscale in letter_scales:
            x_scale = value_scales[letter_scales.index(xscale)]
        else:
            log.warning(
                f"\n[xscale] {xscale} not recognized. Possible scales are: {letter_scales}"
            )
    y_scale = 1.0
    if yscale != "":
        letter_scales = [letter for letter, _ in Scale.values]
        value_scales = [value for _, value in Scale.values]
        if yscale in letter_scales:
            y_scale = value_scales[letter_scales.index(yscale)]
        else:
            log.warning(
                f"\n[yscale] {yscale} not recognized. Possible scales are: {letter_scales}"
            )

    harmonics = [
        (freq[where(power == max(power[1:]))][0], max(power[1:]))
    ]  # don't count the dc component
    harmonics = target_harmonics if bool(target_harmonics) else harmonics
    # add the target harmonics to the plot in case they were folded into the positive frequency axis
    new_freq = append(freq, [harmonics[i][0] for i in range(len(harmonics))])
    freq = sort(new_freq)
    power = append(power, [harmonics[i][1] for i in range(len(harmonics))])[
        argsort(new_freq)
    ]
    if plot_to_terminal and show:
        tplt.plot(freq, power)
        tplt.ylim(min(power), max(power) + abs(max(power)) * 1.1)
        # plot the marks of the harmonics
        colours = cycle(
            ["red+", "gray+", "green+", "white", "magenta+", "cyan+", "yellow+"]
        )
        # line_styles = cycle(["-.", "--", "-.", "-", "--"])
        labels = [
            f"H{x}@{f:.3f} {xscale}{xunit}"
            for (x, f) in enumerate([f for f, _ in harmonics], start=1)
        ]
        """
        tplt.horizontal_line(
            max(power[1:]),
            color="white",
        )
        """
        for color, harmonic, label in zip(colours, harmonics, labels):
            x = harmonic[0]
            y = harmonic[1]
            tplt.plot([x], [y], marker="sd", color=color)
            tplt.text(label, x, y - 0.06 * abs(y), color=color)

        tplt.grid()
        tplt.title(title + f"- H1 Power={max(power[1:]):.2f} ({yscale}{yunit})")
        tplt.xlabel(xlabel)
        tplt.ylabel(ylabel)
        if xlog:
            tplt.xscale("log")
        tplt.theme("dark")
        tplt.show()
        # clear data
        if bool(file_path):
            if not os.path.exists(getParent(file_path)):
                raise FileNotFoundError(
                    f"Directory does not exist : {getParent(file_path)}"
                )
            tplt.savefig(file_path)
        tplt.cld()
    else:
        plt.plot(freq / x_scale, power / y_scale, "b-")
        markerline, _, _ = plt.stem(
            freq / x_scale,
            power / y_scale,
            bottom=min(power / y_scale),
            use_line_collection=True,
            linefmt="b-",
            markerfmt="none",
            basefmt="r-",
        )
        markerline.set_markerfacecolor("none")
        colours = cycle(["red", "brown", "green", "black", "magenta", "cyan", "yellow"])
        # line_styles = cycle(["-.", "--", "-.", "-", "--"])
        labels = [
            f"H{x}@{f/x_scale:.3f} ({xscale}{xunit})"
            for (x, f) in enumerate([f for f, _ in harmonics], start=1)
        ]
        plt.axhline(
            max(power[1:] / y_scale),
            color="k",
            linestyle="--",
            linewidth=3,
            label=f"H1 Power={max(power[1:]/y_scale):.2f} ({yscale}{yunit})",
        )
        for color, harmonic, label in zip(colours, harmonics, labels):
            x = harmonic[0]
            y = harmonic[1]
            plt.plot(x / x_scale, [y / y_scale], "D", color=color, label=label)

        plt.grid()
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend(loc="upper right")
        if xlog:
            plt.xscale("log")
        if show:
            plt.show()
        if bool(file_path):
            if not os.path.exists(getParent(file_path)):
                raise FileNotFoundError(
                    f"Directory does not exist : {getParent(file_path)}"
                )
            plt.savefig(file_path)
    plt.clf()
