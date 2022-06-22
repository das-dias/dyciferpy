from re import X
from dycifer import __version__
from dycifer.read import readSignals
from dycifer.mixed_signals import adcDynamicEval
from dycifer.analog import caosDynamicEval
from dycifer.dycifer import cli
import unittest
from dycifer.utils import plotPrettyFFT
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame


class TestDycifer(unittest.TestCase):
    def test_version(self):
        self.assertTrue(__version__ == "0.1.0")

    def test_readSignals(self):
        file_path = "./resources/data/test_signals.csv"
        # create the test data
        fs = 1e9  # sampling frequency
        ts = 1.0 / fs  # sampling time stamp / period
        f_window = 10e6  # window frequency
        t_window = 1 / f_window
        t = np.arange(0, 1.0 * t_window, ts)  # time axis
        # signal 1
        freq1 = 300e6  # 300 MHz
        s1 = 1.0 * np.sin(2 * np.pi * freq1 * t)  # signal 1
        # signal 2
        freq2 = 600e6  # 500 MHz
        s2 = 2.0 * np.sin(2 * np.pi * freq2 * t)  # signal 2
        # signal 3
        freq3 = 900e6  # 900 MHz
        s3 = 1.5 * np.sin(2 * np.pi * freq3 * t)  # signal 3
        # signal 4 = sum(s1, s2, s3)
        s4 = s1 + s2 + s3
        # plot
        """
        plt.plot(t, s1, label="signal 1")
        plt.plot(t, s2, label="signal 2")
        plt.plot(t, s3, label="signal 3")
        plt.plot(t, s4, label="signal 4")
        plt.legend()
        plt.xlabel("time [s]")
        plt.ylabel("amplitude [v]")
        plt.show()
        """
        # save the signals
        sdf = DataFrame(
            {
                "signal 1": s1,
                "signal 2": s2,
                "signal 3": s3,
                "time [s]": t,
                "signal 4": s4,
            }
        )
        print(sdf.head(5))
        sdf.to_csv(file_path, index=False)
        signals = readSignals(file_path)
        self.assertIsNotNone(signals)
        self.assertEqual(DataFrame, type(signals))
        print(signals.head(5))
        self.assertTrue(signals.reset_index().shape[1] == sdf.shape[1])
        self.assertTrue(signals.shape[0] == sdf.shape[0])
        self.assertTrue(
            np.allclose(
                signals.reset_index().values, sdf[signals.reset_index().columns].values
            )
        )
        file_path_fooling = "./resources/data/fool_test_signals.csv"
        print()
        sdf_fooling = DataFrame(
            {
                "signal 1": s1,
                "signal 2": s2,
                "signal 3": s3,
                "notime [A]": t,
                "signal 4": s4,
            }
        )
        print(sdf_fooling.head(5))
        sdf_fooling.to_csv(file_path_fooling, index=False)
        signals = readSignals(file_path_fooling)
        self.assertIsNotNone(signals)

    def test_adcDynamicEval(self):
        # create the test data
        fs = 10e9  # sampling frequency
        ts = 1.0 / fs  # sampling time stamp / period
        f_window = 10e6  # window frequency
        t_window = 1 / f_window
        t = np.arange(0, 1.0 * t_window, ts)  # time axis
        # signal 1
        res = 6  # bits
        N_dout = 2**res - 1
        vrange = 1.0
        v_step = vrange / N_dout
        # signal 1
        freq1 = 300e6  # 300 MHz
        s = 0.5 * np.sin(2 * np.pi * freq1 * t) + 0.5  # signal 1
        # signal 2
        freq2 = 600e6  # 500 MHz
        # s += 0.2*np.sin(2*np.pi*freq2*t)# signal 2
        # signal 3
        freq3 = 900e6  # 900 MHz
        s += 0.2 * np.sin(2 * np.pi * freq3 * t)  # signal 3
        dout = np.round(s / v_step)
        signals = DataFrame({"time [s]": t, "dout": dout}).set_index("time [s]")
        file_path = "./resources/data/test_signals2.csv"
        signals.to_csv(file_path, index=False)
        spectrum, signal_power, dc_power, sfdr, thd, snr, sndr, enob = adcDynamicEval(
            signals, fs / 5, n_bits=res, signal_span_factor=0.002
        )  # 0.2 % of power spectral density leakage
        self.assertIsNotNone(spectrum)
        self.assertEqual(DataFrame, type(spectrum))
        self.assertAlmostEqual(-6.0517, signal_power, places=3)
        self.assertAlmostEqual(-69.9662, dc_power, places=3)
        self.assertAlmostEqual(7.9485, sfdr, places=3)
        self.assertAlmostEqual(-7.9485, thd, places=3)
        self.assertAlmostEqual(38.5057, snr, places=3)
        self.assertAlmostEqual(7.9447, sndr, places=3)
        self.assertAlmostEqual(1.0273, enob, places=3)

    def test_dycifer_cli_help(self):
        args = ["-h"]
        with self.assertRaises(SystemExit):
            cli(args)
        args = ["--version"]
        with self.assertRaises(SystemExit):
            cli(args)

    def test_dycifer_cli_mixed_signals_help(self):
        args = ["mixedsignals"]
        with self.assertRaises(SystemExit):
            cli(args)
        args = ["analog", "-h"]
        with self.assertRaises(SystemExit):
            cli(args)

    def test_dycifer_cli_mixed_signals_adcDynamicEval(self):
        """_summary_
        Testing the mixed-signals CLI to evaluate the ADC dynamic performance
        with a signals test data that doesn't feature any time stamps, and therefore
        a sampling frequency must be parsed from the command line to effectively retreive the
        correct time distance between each sample.
        """
        args = [
            "mixedsignals",
            "-adc",
            "-s",
            "./resources/data/test_signals2.csv",
            "-fs",
            "10 G",
            "-bit",
            "6",
            "-gt",
            "-o",
            "./resources/tables",
            # "-p",
        ]
        with self.assertRaises(SystemExit):
            cli(args)

    def test_dycifer_cli_mixed_signals_adcDynamicEval_cadence_data(self):
        """_summary_
        Testing the mixed-signals CLI to evaluate the ADC dynamic performance
        with signals provenient directly from Cadence.
        """
        args = [
            "mixedsignals",
            "-adc",
            "-s",
            "./resources/data/fft_points_c2c_256_bin7.csv",
            "-fs",
            "1 G",
            "-gt",
            "-o",
            "./resources/tables_jonny",
            # "-p",
        ]
        with self.assertRaises(SystemExit):
            cli(args)

    def test_dycifer_cli_mixed_signals_adcDynamicEval_textfile_parsing(self):
        """_summary_
        Testing the command line interface parser by executing
        commands retreived directly from a text file.
        """
        args = ["mixedsignals", "@./resources/mixed-signal-run.txt"]
        with self.assertRaises(SystemExit):
            cli(args)

    def test_caosDynamicEval_plotPrettyFFT_multiple(self):
        # create the test data
        fs = 10e9  # sampling frequency
        ts = 1.0 / fs  # sampling time stamp / period
        f_window = 10e6  # window frequency
        t_window = 1 / f_window
        t = np.arange(0, 1.0 * t_window, ts)  # time axis
        # signal 1
        res = 6  # bits
        N_dout = 2**res - 1
        vrange = 1.0
        v_step = vrange / N_dout
        # signal 1
        freq1 = 300e6  # 300 MHz
        s = 1e-3 * np.cos(2 * np.pi * freq1 * t)  # signal 1
        # signal 2
        freq2 = 600e6  # 500 MHz
        s += 1e-4 * np.cos(2 * np.pi * freq2 * t)  # signal 2
        # signal 3
        freq3 = 900e6  # 900 MHz
        s += 1e-5 * np.cos(2 * np.pi * freq3 * t)  # signal 3

        out = s * 1e3 + 0.45
        s += 0.45
        signals = DataFrame({"time [s]": t, "vin": s, "vout": out}).set_index(
            "time [s]"
        )
        file_path = "./resources/data/test_signals3.csv"
        signals.to_csv(file_path, index=False)
        (
            out_spectrum,
            signal_power,
            dc_power,
            gain,
            gain_db,
            sfdr,
            thd,
            snr,
            sndr,
            hd2,
            hd3,
        ) = caosDynamicEval(
            signals,
            "vin",
            "vout",
            signal_span_factor=0.002,
            noise_power=1,
            downsampling=5,
        )  # 0.2 % of power spectral density leakage
        self.assertIsNotNone(out_spectrum)
        self.assertEqual(DataFrame, type(out_spectrum))
        kwargs = {
            "linefmt": "b-",
            "markerfmt": "bD",
            "basefmt": "k-",
        }
        """
        plotPrettyFFT(
            out_spectrum.index[out_spectrum.index >= 0],
            out_spectrum["power_db"][out_spectrum.index >= 0],
            show=True,
            **kwargs
        )
        """
        self.assertAlmostEqual(signal_power, -5.987259500627048, places=2)
        self.assertAlmostEqual(dc_power, -6.920592008427765, places=2)
        self.assertAlmostEqual(gain, 1003.8458331687908, places=2)
        self.assertAlmostEqual(sfdr, 19.514957781276006, places=2)
        self.assertAlmostEqual(thd, -19.488729725548698, places=2)
        self.assertAlmostEqual(snr, 26.2454720617147, places=2)
        self.assertAlmostEqual(sndr, 18.65721282743459, places=2)
        self.assertAlmostEqual(hd2, -19.514957781276006, places=2)
        self.assertAlmostEqual(hd3, -41.69201928902894, places=2)


if __name__ == "__main__":
    unittest.main()
