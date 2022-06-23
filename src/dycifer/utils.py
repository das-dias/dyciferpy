import os


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
    NOTE:
        kwargs example:
        kwargs = {
            "linefmt":"b-",
            "markerfmt":"bD",
            "basefmt":"r-",
        }
    """
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
    plt.plot(freq, power, "b-")
    markerline, _, _ = plt.stem(
        freq,
        power,
        bottom=min(power),
        use_line_collection=True,
        linefmt="b-",
        markerfmt="none",
        basefmt="r-",
    )
    markerline.set_markerfacecolor("none")
    colours = cycle(["red", "brown", "green", "black", "magenta", "cyan", "yellow"])
    # line_styles = cycle(["-.", "--", "-.", "-", "--"])
    labels = [
        f"H{x}@{f/1e9:.3f} GHz"
        for (x, f) in enumerate([f for f, _ in harmonics], start=1)
    ]
    plt.axhline(
        max(power[1:]),
        color="k",
        linestyle="--",
        linewidth=3,
        label=f"H1 Power={max(power[1:]):.2f} (dB)",
    )
    for color, harmonic, label in zip(colours, harmonics, labels):
        x = harmonic[0]
        y = harmonic[1]
        plt.plot(x, [y], "D", color=color, label=label)

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
