from loguru import logger as log
from dycifer import __version__, __author__, __email__
import sys
import os
import re
import argparse
import traceback
from dycifer.analog import analogDynamicEval
from dycifer.mixed_signals import mixedSignalsDynamicEval

# define the subparsers
__cmds = {
    "-ms": (
        "mixedsignals",
        "Mixed Signals dynamic performance evaluation",
        mixedSignalsDynamicEval,
    ),
    "-a": (
        "analog",
        "Analog integrated circuits dynamic performance evaluation",
        analogDynamicEval,
    ),
}
# define the arguments of each subparser
__cmd_args = {
    "-ms": {
        "-adc": (
            "--analog-to-digital",
            "Analog to Digital Converter (ADC) dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-dac": (
            "--digital-to-analog",
            "Digital to Analog Converter (DAC) dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-sda": (
            "--sigma-delta-adc",
            "Sigma Delta ADC dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-sdd": (
            "--sigma-delta-dac",
            "Sigma Delta DAC dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-fs": (
            "--sampling-frequency",
            "Sampling frequency of the parsed signals",
            "FREQUENCY",
            str,
            "",
        ),  # sampling frequency of the parsed signals is obligatory
        "-bit": (
            "--bit-resolution",
            "Bitwise resolution of the ADC/DAC",
            "#BITS",
            int,
            "opt",
        ),
        "-vs": (
            "--voltage-source",
            "Voltage source of the ADC/DAC",
            "VOLTAGE",
            float,
            "opt",
        ),
        "-nh": (
            "--harmonics",
            "Number of harmonics of the output signal power considered during THD computation",
            "#HARMONICS",
            int,
            "opt",
        ),
        "-ss": (
            "--signal-span",
            "Spectral dispertion factor of the output signal power",
            "DECIMAL",
            float,
            "opt",
        ),
        "-a": (
            "--ascending",
            "Signals of each Bit are in ascending bit order or not",
            "",
            bool,
            "opt",
        ),
    },
    "-a": {
        "-daos": (
            "--discrete-aos",
            "Discrete Amplitude Output system (DAOS) dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-caos": (
            "--continuous-aos",
            "Continuous Amplitude Output system (CAOS) dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-is": (
            "--input-signal",
            "Target output signal of the analysis",
            "NAME",
            str,
            "opt",
        ),
        "-fs": (
            "--sampling-frequency",
            "Sampling frequency of the parsed signals",
            "FREQUENCY",
            str,
            "",
        ),  # sampling frequency of the parsed signals is obligatory
        "-os": (
            "--output-signal",
            "Target output signal of the analysis",
            "NAME",
            str,
            "",
        ),
        "-wf": (
            "--waveform",
            'Target waveform type ("default": modulated pulse wave, "pulse": pulse wave, "sawtooth": sawtooth wave)',
            "TYPE",
            str,
            "opt",
        ),
        "-rl": (
            "--risetime-level",
            "Rise Time Computation Upper Level (usual: [0.9, 0.95, 0.99], default: 0.9)",
            "FLOAT[0;1]",
            float,
            "opt",
        ),
        "-nh": (
            "--harmonics",
            "Number of harmonics of the output signal power considered during THD computation",
            "#HARMONICS",
            int,
            "opt",
        ),
        "-ss": (
            "--signal-span",
            "Spectral dispertion factor of the output signal power",
            "DECIMAL",
            float,
            "opt",
        ),
    },
    "all": {
        "-s": (
            "--signals",
            "Path of the file containing the time-series signals to analyse",
            "FILEPATH",
            str,
            "",
        ),
        "-o": (
            "--output-file",
            "Specify the output filename/filepath for the resulting output files",
            "FILEPATH",
            str,
            "opt",
        ),
        "-np": (
            "--noise-power",
            "Power of the noise signal added to the target signals (in dBm)",
            "NOISE_DBM",
            float,
            "opt",
        ),
        "-p": (
            "--plot",
            "Boolean flag to indicate the programme to plot or not the resulting analysis graphs",
            "",
            bool,
            "opt",
        ),
        "-gt": (
            "--generate-table",
            "Boolean flag to indicate the programme to generate a markdown and a latex table with the resulting analysis data",
            "",
            bool,
            "opt",
        ),
        "-pt": (
            "--plot-to-terminal",
            "Plot the resulting analysis graphs to the terminal in ASCII mode",
            "",
            bool,
            "opt",
        ),
    },
}


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


def setupParser(
    cmds: dict,
    args: dict,
    author: str = "",
    email: str = "",
    prog_name: str = "",
    prog_vers: str = "",
    desc: str = "",
    **kwargs,
) -> argparse.ArgumentParser:
    from colorama import init, Fore, Back, Style

    """_summary_
    Sets up the command line parser.
    Args:
        cmds (dict): dictionary of commands defining the callbacks to each subparser
        args (dict): dictionary of arguments for each command/subparser callback function
        entrymsg (str): entry message for the parser
        progname (str): program name
        progvers (str): program version
        desc (str): program description
    Returns:
        argparse.ArgumentParser: console argument parser object
    """
    if os.environ.get("OS", "") == "Windows_NT":
        init()  # init colorama
    gray, cyan, green, blue = Fore.WHITE, Fore.CYAN, Fore.GREEN, Fore.BLUE

    # setup the messages formatter class for the console
    col_base = gray if "col_base" not in kwargs else kwargs["col_base"]
    col_usage = cyan if "col_usage" not in kwargs else kwargs["col_usage"]
    col_option = cyan if "col_option" not in kwargs else kwargs["col_option"]
    col_caps = green if "col_caps" not in kwargs else kwargs["col_caps"]
    col_prog = green if "col_prog" not in kwargs else kwargs["col_prog"]

    def msg_formatter(msg, color=gray):
        return f"{color}{msg}{Style.RESET_ALL}"

    def entryMsg(prog_name: str = "", author: str = "", email: str = "") -> str:
        from pyfiglet import figlet_format

        """_summary_
        Returns the application entry message as a string.
        Returns:
            str: entry message
        """
        figlet_color = green
        figlet_art = (
            figlet_format(f"{prog_name.upper()}", font="alligator", justify="center")
            if bool(prog_name)
            else ""
        )
        msgs = [
            f"{msg_formatter(figlet_art, color=figlet_color)}",
            "by " + author + " (" + email + ")"
            if (bool(author) and bool(email))
            else "",
        ]
        max_ch = max([len(submsg) for submsg in [msgs[0][-1]] + msgs[1:]]) + 2
        sep_color = green
        sep = "#"
        # sep_msg = msg_formatter(sep * max_ch, color=sep_color)
        # ret = f"{sep_msg}" + "\n"
        ret = ""
        ret += msgs[0]
        for msg in msgs[1:]:
            ret += msg + " " * (max_ch - len(msg)) + "\n"
        # ret += f"{sep_msg}" + "\n"
        return ret

    def make_wide(formatter, w: int = 120, h: int = 36, max_help_position: int = 30):
        import warnings

        """Return a wider HelpFormatter, if possible."""
        try:
            # https://stackoverflow.com/a/5464440
            # beware: "Only the name of this class is considered a public API."
            kwargs = {
                "width": w,
                "max_help_position": h,
                "max_help_position": max_help_position,
            }
            formatter(None, **kwargs)
            return lambda prog: formatter(prog, **kwargs)
        except TypeError:
            warnings.warn("Argparse help formatter failed, falling back.")
            return formatter

    class FormattedConsoleParser(argparse.ArgumentParser):
        def _print_message(self, message, file=None):
            if message:
                if message.startswith("usage"):
                    print(entryMsg(prog_name, author, email))

                    message = f"{msg_formatter(prog_name, color=col_prog)} {prog_vers}\n\n{message}"
                    message = re.sub(
                        r"(-[a-z]+\s*|\[)([A-Z]+)(?=]|,|\s\s|\s\.)",
                        r"\1{}\2{}".format(col_caps, Style.RESET_ALL),
                        message,
                    )
                    message = re.sub(
                        r"((-|--)[a-z]+)",
                        r"{}\1{}".format(col_option, Style.RESET_ALL),
                        message,
                    )

                    usage = msg_formatter("USAGE", color=col_usage)
                    message = message.replace("usage", f"{usage}")

                    flags = msg_formatter("FLAGS", color=col_usage)
                    message = message.replace("options", f"{flags}")

                    progg = msg_formatter(self.prog, color=col_prog)
                    message = message.replace(self.prog, f"{progg}")
                message = f"{msg_formatter(message.strip(), color=col_base)}"
                print(message)

    parser = FormattedConsoleParser(
        prog=prog_name,
        description=desc,
        formatter_class=make_wide(argparse.HelpFormatter, max_help_position=45),
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{msg_formatter(prog_name, color=col_prog)} v{msg_formatter(prog_vers, color=col_base)}",
    )
    # mutually exclusive arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--quiet", action="store_true", help="quiet run")
    group.add_argument("--verbose", action="store_true", help="verbose run")
    subparsers = parser.add_subparsers()
    for cmd, (cmd_name, cmd_desc, cmd_callback) in cmds.items():
        subparser = subparsers.add_parser(
            cmd_name,
            help=cmd_desc,
            formatter_class=make_wide(argparse.HelpFormatter, max_help_position=45),
            fromfile_prefix_chars="@",  # to run the script from a text file
        )
        subparser.set_defaults(func=mapSubparserToFun(cmd_callback, subparser))
        optional = subparser._action_groups.pop()
        required = subparser.add_argument_group("required arguments")
        subgroup = subparser.add_mutually_exclusive_group()
        if bool(args.get("all")):
            for arg, (
                arg_literal,
                arg_desc,
                arg_metavar,
                arg_type,
                arg_opt,
            ) in args["all"].items():
                if arg_type in [bool, None]:
                    subparser.add_argument(
                        arg,
                        arg_literal,
                        action="store_true",
                        required=False if arg_opt == "opt" else True,
                        help=arg_desc,
                    )
                else:
                    if arg_opt in ["opt", "optional"]:
                        optional.add_argument(
                            arg,
                            arg_literal,
                            nargs=1,
                            type=arg_type,
                            help=arg_desc,
                            metavar=arg_metavar,
                        )
                    else:
                        required.add_argument(
                            arg,
                            arg_literal,
                            nargs=1,
                            type=arg_type,
                            help=arg_desc,
                            required=True,
                            metavar=arg_metavar,
                        )
        for arg, (arg_literal, arg_desc, arg_metavar, arg_type, arg_opt) in args[
            cmd
        ].items():
            if arg_type in [bool, None]:
                subgroup.add_argument(
                    arg,
                    arg_literal,
                    action="store_true",
                    required=False if arg_opt == "opt" else True,
                    help=arg_desc,
                )
            else:
                if arg_opt in ["opt", "optional"]:
                    optional.add_argument(
                        arg,
                        arg_literal,
                        nargs=1,
                        type=arg_type,
                        help=arg_desc,
                        metavar=arg_metavar,
                    )
                else:
                    required.add_argument(
                        arg,
                        arg_literal,
                        nargs=1,
                        type=arg_type,
                        help=arg_desc,
                        required=True,
                        metavar=arg_metavar,
                    )
        subparser._action_groups.append(optional)
    return parser


def cli(argv=None) -> None:
    """_summary_
    Command Line Interface entry point for user interaction.
    Args:
        argv (list, optional): Commands parsed as method input for CLI testing purposes. Defaults to None.
    """
    if argv is None:
        argv = sys.argv[1:]
    parser = setupParser(
        __cmds,
        __cmd_args,
        author=__author__,
        email=__email__,
        prog_vers=__version__,
        prog_name="dycifer",
        desc="Dynamic Integrated Circuit Performance Evaluation Tool written in Python",
    )
    subparsers = [tok for tok in __cmds.keys()] + [tok[0] for tok in __cmds.values()]
    if len(argv) == 0:  # append "help" if no arguments are given
        argv.append("-h")
    elif argv[0] in subparsers:
        if len(argv) == 1:
            argv.append("-h")  # append help when only
            # one positional argument is given
    try:
        args = parser.parse_args(argv)
        try:
            args.func(argv)
        except Exception as e:
            log.error(traceback.format_exc())
    except argparse.ArgumentError as e:  # catching unknown arguments
        log.warning(e)
    except Exception as e:
        log.error(traceback.format_exc())
    sys.exit(1)  # traceback successful command run
