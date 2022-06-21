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


def mapSubparserToFun(func, subparser):
    from functools import wraps

    """_summary_
    Maps subparser to callback function
    Args:
        func (Function): callback function
        subparser (_type_): subparser object
    Returns:
        result (_type_): result of the callback function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(subparser, *args, **kwargs)

    return wrapper


def plotPrettyFFT(
    freq,
    power,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    file_path: str = None,
    xlog: bool = False,
    show: bool = False,
):
    """_summary_
    Plot a pretty FFT plot
    Args:
        freq (np.array/list): frequency array
        power (np.array/list): power array
        title (str)     : title of the plot
        xlabel (str)    : x-axis label
        ylabel (str)    : y-axis label
        file_path (str) : path to save the plot
        xlog (bool)     : log scale
        show (bool)     : show the plot
    """
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
    from numpy import min, where
    import pdb

    plt.rc("axes", titlesize=14)  # fontsize of the axes title
    plt.rc("axes", labelsize=12)  # fontsize of the x and y labels
    plt.rc("xtick", labelsize=12)  # fontsize of the tick labels
    plt.rc("ytick", labelsize=12)  # fontsize of the tick labels
    plt.rc("legend", fontsize=11)  # legend fontsize
    plt.rc("font", size=11)  # controls default text sizes
    # define font family to use for all text
    rcParams["font.family"] = "serif"
    # plt.figure(figsize=(8,6))
    markerline, stemlines, baseline = plt.stem(
        freq, power, bottom=min(power), linefmt="b-", markerfmt="bD", basefmt="k-."
    )
    markerline.set_markerfacecolor("none")
    # highlight the spectral signal components
    signal_freq = freq[where(power == max(power[1:]))]  # don't count the dc component
    colours = ["r", "b", "g", "k", "m"]
    line_styles = ["-.", "--", "-.", "-", "--"]
    for c, ls, f in zip(colours, line_styles, signal_freq):
        plt.axvline(
            f,
            ymin=min(power[1:]),
            color=c,
            linestyle=ls,
            linewidth=3,
            label=f"Fundamnetal Harmonic @ {f/1e9:.3}G Hz",
        )
    plt.axhline(
        max(power[1:]),
        color="k",
        linestyle="--",
        linewidth=3,
        label=f"Fundamental Harmonic Power = {max(power[1:]):.2f} (dB)",
    )
    # pdb.set_trace()
    plt.grid()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc="lower right")
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
