from loguru import logger as log
from dycifer import __version__, __author__, __email__
import sys
from pyfiglet import Figlet
import argparse
import traceback
from dycifer.utils import getParent, mapSubparserToFun
from dycifer.analog import analogDynamicEval
from dycifer.mixed_signals import mixedSignalsDynamicEval

# define the subparsers
__cmds = {
    "-ms": (
        "mixed-signals",
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
            "Analog-to-Digital Converter dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-dac": (
            "--digital-to-analog",
            "Digital-to-Analog Converter dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-sda": (
            "--sigma-delta-adc",
            "Sigma-Delta Analog-to-Digital Converter dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-sdd": (
            "--sigma-delta-dac",
            "Sigma-Delta Digital-to-Analog Converter dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-fs": (
            "--sampling-frequency",
            "Sampling frequency of the parsed signals",
            "<frequency>",
            str,
            "",
        ),  # obrigatório especificar a frequência de amostragem
        "-bit": (
            "--bit-resolution",
            "Bit-wise resolution of the ADC/DAC",
            "<#bits>",
            int,
            "opt",
        ),
        "-vs": (
            "--voltage-source",
            "Voltage source of the ADC/DAC",
            "<voltage>",
            float,
            "opt",
        ),
        "-nh": (
            "--harmonics",
            "Number of harmonics of the output signal power considered during THD computation",
            "<#harmonics>",
            int,
            "opt",
        ),
        "-ss": (
            "--signal-span",
            "Spectral dispertion factor of the output signal power",
            "<decimal>",
            float,
            "opt",
        ),
        "-a": (
            "--ascending",
            "Boolean value indicating if the signals of each Bit are in ascending bit order or not",
            "",
            bool,
            "opt",
        ),
    },
    "-a": {
        "-cmp": (
            "--comparator",
            "Compararator dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-scc": (
            "--switch-capacitor-circuit",
            "Switch Capacitor Circuit dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
        "-amp": (
            "--amplifier",
            "Amplifier dynamic performance evaluation",
            "",
            bool,
            "opt",
        ),
    },
    "all": {
        "-s": (
            "--signals",
            "Specify the input path of the file containing the time-series signals to analyse",
            "<filepath>",
            str,
            "",
        ),
        "-o": (
            "--output-dir",
            "Specify the output directory for the resulting output files",
            "<directory-path>",
            str,
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
    },
}


def setupParser(cmds: dict, args: dict) -> argparse.ArgumentParser:
    """_summary_
    Sets up the command line parser.
    Args:
        cmds (dict): dictionary of commands defining the callbacks to each subparser
        cmd_args (dict): dictionary of arguments for each command/subparser callback function
    Returns:
        argparse.ArgumentParser: console argument parser object
    """
    parser = argparse.ArgumentParser(
        description="DYCIFER - Dynamic Circuits Performance Evaluation Tool"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"DYCIFER v{__version__}"
    )
    # mutually exclusive arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", action="store_true", help="quiet run")
    group.add_argument("-vb", "--verbose", action="store_true", help="verbose run")
    subparsers = parser.add_subparsers()
    for cmd, (cmd_name, cmd_desc, cmd_callback) in cmds.items():
        subparser = subparsers.add_parser(cmd_name, help=cmd_desc)
        subparser.set_defaults(func=mapSubparserToFun(cmd_callback, subparser))
        subgroup = subparser.add_mutually_exclusive_group()
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
                subparser.add_argument(
                    arg,
                    arg_literal,
                    nargs=1,
                    type=arg_type,
                    help=arg_desc,
                    required=False if arg_opt == "opt" else True,
                    metavar=arg_metavar if arg_metavar != "<>" else "",
                )
        if bool(__cmd_args.get("all")):
            for arg, (
                arg_literal,
                arg_desc,
                arg_metavar,
                arg_type,
                arg_opt,
            ) in __cmd_args["all"].items():
                if arg_type in [bool, None]:
                    subparser.add_argument(
                        arg,
                        arg_literal,
                        action="store_true",
                        required=False if arg_opt == "opt" else True,
                        help=arg_desc,
                    )
                else:
                    subparser.add_argument(
                        arg,
                        arg_literal,
                        nargs=1,
                        type=arg_type,
                        help=arg_desc,
                        required=False if arg_opt == "opt" else True,
                        metavar=arg_metavar if arg_metavar != "<>" else "",
                    )
    return parser


def entryMsg() -> str:
    """_summary_
    Returns the application entry message as a string.
    Returns:
        str: entry message
    """
    msgs = [
        Figlet(font="slant").renderText("DYCIFER"),
        "Dynamic Circuits Performance Evaluation Tool written in Python",
        "by " + __author__ + " (" + __email__ + ")",
    ]
    max_ch = max([len(msg) for msg in msgs[1:]]) + 2
    sep = "#"
    ret = sep * (max_ch) + "\n"
    ret += msgs[0]
    for msg in msgs[1:]:
        ret += " " + msg + " " * (max_ch - len(msg)) + "\n"
    ret += sep * (max_ch) + "\n"
    return ret


def cli(argv=None) -> None:
    """_summary_
    Command Line Interface entry point for user interaction.
    Args:
        argv (list, optional): Commands parsed as method input for CLI testing purposes. Defaults to None.
    """
    print(entryMsg())
    if argv is None:
        argv = sys.argv[1:]
    parser = setupParser(__cmds, __cmd_args)
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
