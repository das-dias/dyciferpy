from re import X
from turtle import color
from dycifer.read import readSignals
from dycifer.analog import caosDynamicEval
from dycifer.dycifer import cli
import unittest
from dycifer.utils import plotPrettyFFT
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame


class TestCAOSDynamicEval(unittest.TestCase):
    def test_caosDynamicEval(self):
        # create the test data
        fs = 1e9  # sampling frequency
        file_path = "./resources/data/test_signals3.csv"
        signals = readSignals(file_path)
        # equivalent but more general
        plt.subplot(2, 1, 1)
        plt.plot(signals.index, signals["vout"], color="red", label="vout", ls="-")
        plt.ylabel("Output Signal [V]")
        plt.grid()
        plt.xlim([0.0, 10 / fs])
        plt.legend()
        plt.subplot(2, 1, 2)
        plt.plot(signals.index, signals["vin"], color="blue", label="vin", ls="--")
        plt.ylabel("Input Signal [V]")
        plt.xlabel("Time [s]")
        plt.grid()
        plt.xlim([0.0, 10 / fs])
        plt.legend()
        plt.show()
        plt.clf()
        (
            out_spectrum,
            target_harmonics,
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
            fs,
            "vout",
            input_signal_name="vin",
            signal_span_factor=0.01,
            noise_power=0.0,
        )  # 0.2 % of power spectral density leakage
        self.assertIsNotNone(out_spectrum)
        self.assertEqual(DataFrame, type(out_spectrum))
        plotPrettyFFT(
            out_spectrum.index[out_spectrum.index >= 0],
            out_spectrum["power_db"][out_spectrum.index >= 0],
            show=True,
            target_harmonics=target_harmonics,
            title="Output Spectrum",
            xlabel="Frequency (GHz)",
            ylabel="Power (dB)",
            xscale="G",
        )
