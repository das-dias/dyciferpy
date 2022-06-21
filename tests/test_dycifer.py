from re import X
from dycifer import __version__
from dycifer.read import readSignals
from dycifer.mixed_signals import adcDynamicEval
from dycifer.dycifer import cli
import unittest
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
        plt.stem(
            spectrum[spectrum.index > 0].index,
            spectrum["power_db"][spectrum.index > 0].values,
            bottom=spectrum["power_db"].min(),
        )
        plt.xlabel("frequency (Hz)")
        plt.ylabel("power (dB)")
        plt.title("Output Signal Power Spectrum (dB)")
        plt.grid()
        plt.show()
        print(f"Signal Power = {signal_power} [dB]")
        print(f"Signal DC Power = {dc_power} [dB]")
        print(f"SFDR = {sfdr} [dB]")
        print(f"THD = {thd} [dB]")
        print(f"SNR = {snr} [dB]")
        print(f"SNDR = {sndr} [dB]")
        print(f"ENOB = {enob} [dB]")

    def test_dycifer_cli_help(self):
        args = ["-h"]
        with self.assertRaises(SystemExit):
            cli(args)
        args = ["--version"]
        with self.assertRaises(SystemExit):
            cli(args)

    def test_dycifer_cli_mixed_signals_help(self):
        args = ["mixed-signals"]
        with self.assertRaises(SystemExit):
            cli(args)
        args = ["mixed-signals", "-h"]
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
            "mixed-signals",
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
            "-p",
        ]
        with self.assertRaises(SystemExit):
            cli(args)

    def test_dycifer_cli_mixed_signals_adcDynamicEval_cadence_data(self):
        """_summary_
        Testing the mixed-signals CLI to evaluate the ADC dynamic performance
        with signals provenient directly from Cadence.
        """
        args = [
            "mixed-signals",
            "-adc",
            "-s",
            "./resources/data/fft_points_c2c_256_bin7.csv",
            "-fs",
            "1 G",
            "-gt",
            "-o",
            "./resources/tables_jonny",
            "-p",
        ]
        with self.assertRaises(SystemExit):
            cli(args)


if __name__ == "__main__":
    unittest.main()
