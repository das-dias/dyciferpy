from re import X
from dycifer.read import readSignals
from dycifer.mixed_signals import adcDynamicEval
from dycifer.dycifer import cli
import unittest
from dycifer.utils import plotPrettyFFT
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame


class TestADCDynamicEval(unittest.TestCase):
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
        (
            spectrum,
            target_harmonics,
            signal_power,
            dc_power,
            sfdr,
            thd,
            snr,
            sndr,
            enob,
            hd2,
            hd3,
        ) = adcDynamicEval(
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

    def test_adcDynamicEval_adc4bit(self):
        # import the test data
        filepath = "./resources/data/fft_points_c2c_256_x2_bin11_noise.csv"
        signals = readSignals(filepath)
        fs = 0.6e9
        # plot the received signals
        colors = ["red", "blue", "green", "black", "yellow", "magenta", "orange"]
        linestyles = ["solid", "dashed", "dashdot", "solid", "dashed", "dotted"]
        for signal, color, ls in zip(signals.columns, colors, linestyles):
            plt.plot(
                signals.index, signals[signal], label=signal, color=color, linestyle=ls
            )
        print(signals.head())
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude (V)")
        plt.xlim([0.0, 10 / fs])
        plt.legend(loc="lower right")
        plt.grid()
        plt.show()
        plt.clf()
        # perform adcDynamicEval
        (
            spectrum,
            target_harmonics,
            signal_power,
            dc_power,
            sfdr,
            thd,
            snr,
            sndr,
            enob,
            hd2,
            hd3,
        ) = adcDynamicEval(
            signals, fs, signal_span_factor=0.002
        )  # 0.2 % of power spectral density leakage
        # plot spectrum
        plotPrettyFFT(
            spectrum.index[spectrum.index >= 0],
            spectrum["power_db"][spectrum.index >= 0],
            title="Spectrum",
            xlabel="Frequency (GHz)",
            ylabel="Power (dB)",
            target_harmonics=target_harmonics,
            show=True,
            xscale="G",  # gigahertz
        )


if __name__ == "__main__":
    unittest.main()
