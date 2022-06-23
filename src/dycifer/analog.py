import os
import traceback
from loguru import logger as log
from pandas import DataFrame
import numpy as np
from dycifer.utils import plotPrettyFFT
from dycifer.read import readSignals
from modelling_utils import stof, timer
from enum import Enum


def analogDynamicEval(subparser, *args, **kwargs):
    """_summary_
    Dynamic performance evaluation of Analog integrated circuits
    """
    import warnings

    warnings.filterwarnings("ignore")  # supress pandas warnings
    """_summary_
    Dynamic performance evaluation of Mixed Signals circuits
    """
    argv = None
    # read data
    sysargs = args[0]
    try:
        argv = subparser.parse_args(sysargs[1:])
    except Exception as e:
        log.error(traceback.format_exc())
    # from the signals argument (containing the signals file filepath)
    # extract the signals
    signals = readSignals(argv.signals[0])
    if argv.continuous_aos:
        input_signal = argv.input_signal[0] if bool(argv.input_signal) else None
        output_signal = argv.output_signal[0]
        harmonics = argv.harmonics[0] if bool(argv.harmonics) else 7
        signal_span = argv.signal_span[0] if bool(argv.signal_span) else 0.0
        noise_power = argv.noise_power[0] if bool(argv.noise_power) else -1.0
        # pdb.set_trace()
        # perform dynamic performance evaluation
        (
            spectrum,
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
            output_signal,
            input_signal_name=input_signal,
            harmonics=harmonics,
            signal_span_factor=signal_span,
            noise_power=noise_power,
        )
        # prepare to plot resulting information
        dynamic_eval_indicators = DataFrame(
            data={
                "Output Signal Power (dB)": signal_power,
                "Output DC Power (dB)": dc_power,
                "Gain (out/in)": gain,
                "Gain (dB)": gain_db,
                "SFDR (dB)": sfdr,
                "THD (dB)": thd,
                "SNR (dB)": snr,
                "SNDR (dB)": sndr,
                "HD2": hd2,
                "HD3": hd3,
            },
            index=["Dynamic Evaluation Indicators"],
        )
        if argv.plot:
            plotPrettyFFT(
                spectrum[
                    spectrum.index.values >= 0
                ].index,  # plot only positive frequencies spectrum
                spectrum[spectrum.index.values >= 0]["power_db"],
                title="Signal Spectrum (dB)",
                xlabel="Frequency (Hz)",
                ylabel="Power (dB)",
                show=True,
                xlog=False,
                target_harmonics=target_harmonics,
            )
        if bool(argv.output_file):
            plotPrettyFFT(
                spectrum[
                    spectrum.index >= 0
                ].index,  # plot only positive frequencies spectrum
                spectrum[spectrum.index.values >= 0]["power_db"],
                title="Signal Spectrum (dB)",
                xlabel="Frequency (Hz)",
                ylabel="Power (dB)",
                show=False,
                file_path=argv.output_file[0] + ".png",
                target_harmonics=target_harmonics,
            )
            if argv.generate_table:
                tablename = argv.output_file[0]
                dynamic_eval_indicators.to_csv(tablename + ".csv")
                dynamic_eval_indicators.to_json(tablename + ".json")
                dynamic_eval_indicators.to_markdown(tablename + ".md")
                dynamic_eval_indicators.to_latex(tablename + ".tex")
        # print indicators to console
        print()
        print(dynamic_eval_indicators.T)
    elif bool(argv.discrete_aos):
        wave_type = argv.waveform[0] if bool(argv.waveform) else "default"
        upper_level = argv.risetime_level[0] if bool(argv.risetime_level) else 0.9
        input_signal = argv.input_signal[0] if bool(argv.input_signal) else None
        output_signal = argv.output_signal[0]
        harmonics = argv.harmonics[0] if bool(argv.harmonics) else 7
        signal_span = argv.signal_span[0] if bool(argv.signal_span) else 0.0
        noise_power = argv.noise_power[0] if bool(argv.noise_power) else -1.0
        (
            spectrum,
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
            rise_time,
            bandwidth,
        ) = daosDynamicEval(
            signals,
            output_signal,
            input_signal_name=input_signal,
            harmonics=harmonics,
            signal_span_factor=signal_span,
            noise_power=noise_power,
            levels=(0.1, upper_level),
            wave_type=wave_type,
            show_rise_time_eval=argv.plot,
        )
        # prepare to plot resulting information
        dynamic_eval_indicators = DataFrame(
            data={
                "Output Signal Power (dB)": signal_power,
                "Output DC Power (dB)": dc_power,
                "Gain (out/in)": gain,
                "Gain (dB)": gain_db,
                "SFDR (dB)": sfdr,
                "THD (dB)": thd,
                "SNR (dB)": snr,
                "SNDR (dB)": sndr,
                "HD2": hd2,
                "HD3": hd3,
                f"Rise Time[{100*upper_level}%] (ns)": rise_time / 1e-9,
                "Bandwidth (GHz)": bandwidth / 1e9,
            },
            index=["Dynamic Evaluation Indicators"],
        )
        if argv.plot:
            plotPrettyFFT(
                spectrum[
                    spectrum.index.values >= 0
                ].index,  # plot only positive frequencies spectrum
                spectrum[spectrum.index.values >= 0]["power_db"],
                title="Signal Spectrum (dB)",
                xlabel="Frequency (Hz)",
                ylabel="Power (dB)",
                show=True,
                xlog=False,
                target_harmonics=target_harmonics,
            )
        if bool(argv.output_file):
            plotPrettyFFT(
                spectrum[
                    spectrum.index >= 0
                ].index,  # plot only positive frequencies spectrum
                spectrum[spectrum.index.values >= 0]["power_db"],
                title="Signal Spectrum (dB)",
                xlabel="Frequency (Hz)",
                ylabel="Power (dB)",
                show=False,
                file_path=argv.output_file[0] + ".png",
                target_harmonics=target_harmonics,
            )
            if argv.generate_table:
                tablename = argv.output_file[0]
                dynamic_eval_indicators.to_csv(os.path.join(tablename, ".csv"))
                dynamic_eval_indicators.to_json(os.path.join(tablename, ".json"))
                dynamic_eval_indicators.to_markdown(os.path.join(tablename, ".md"))
                dynamic_eval_indicators.to_latex(os.path.join(tablename, ".tex"))
        # print indicators to console
        print()
        print(dynamic_eval_indicators.T)
    else:
        raise ValueError(
            "No analog system class was specified was specified. Missing: --caos or --daos"
        )
    print("\nPerformance evaluation finished.")
    return


@timer
def caosDynamicEval(
    signals: DataFrame,
    output_signal_name: str,
    input_signal_name: str = None,
    harmonics: int = 7,
    signal_span_factor: float = 0.0,
    noise_power: float = -1.0,
    downsampling: int = 1,
) -> tuple[DataFrame, float, float, float, float, float, float, float, float]:
    """_summary_
    Dynamic performance evaluation of Continuous Analog Output Systems (CAOS)
    Args:
        signals (DataFrame): The time series data with all the correspondant signals.
        harmonics (int, optional): The number of harmonics to be used in the CAOS. Defaults to 7.
        signal_span_factor (float, optional): The factor to be used to scale the signal span. Defaults to 0.0.
        noise_power (float, optional): The noise power to be used in the CAOS. Defaults to -1.0.
        output_signal_name (str): The name of the output signal.
        input_signal_name (str, optional): The name of the input signal. Defaults to None. In no input signal is provided,
        the Gain of the system will not be computed.
    Returns:
        tuple[DataFrame, float, float, float, float, float, float, float]: The CAOS performance evaluation results.
            DataFrame: The frequency spectrum of the CAOS output signal in volt, volt squared (power in watt) and decibels.
            float(1): Output Signal's power in decibels
            float(2): Output Signal's DC power (in dB)
            float(3): Gain in linear scale
            float(4): Gain in dB
            float(5): Spurious Free Dynamic Range (SFDR) metric
            float(6): Total Harmonic Distortion (THD) metric
            float(7): Signal to Noise Ratio (SNR) metric
            float(8): Signal to Noise & Distortion Ratio (SNNDR) metric
            float(9): Fractional Second-Harmonic Distortion (HD2) metric
            float(10): Fractional Third-Harmonic Distortion (HD3) metric
    """
    if not bool(signals.index.name):
        raise ValueError("The signals DataFrame must have time axis.")
    if not (output_signal_name in signals.columns):
        raise ValueError(f"{output_signal_name} does not belong to the parsed signals.")
    # perform downsampling if so was chosen
    signals = signals[::downsampling]
    ts = signals.index.values[1] - signals.index.values[0]
    fs = 1.0 / ts
    n_samples = len(signals.index)
    if noise_power > 0:
        noise_watt = (10 ** (noise_power / 10)) * 1e-3
        signals[output_signal_name] = signals[output_signal_name] + np.random.normal(
            0, np.sqrt(noise_watt), size=n_samples
        )
    vout = np.abs(
        np.fft.fftshift(np.fft.fft(signals[output_signal_name].values) / n_samples)
    )  # [V]
    freq = np.fft.fftshift(np.fft.fftfreq(len(vout), ts))  # [Hz]
    power = (
        vout * vout
    )  # [V^2] - square the voltage spectrum to obtain the power spectrum
    power_db = 10 * np.log10(power)  # [dB] - convert the power spectrum to dB
    spectrum = DataFrame(
        index=freq, data={"vout": vout, "power": power, "power_db": power_db}
    )
    # positive frequencies spectrum
    pspectrum = spectrum[spectrum.index >= 0].copy()
    # ********************************************
    # Obtaining the ADC's output signal power
    # ********************************************
    # determine the span of the signal's spectrum to consider it's total dispersed power
    span = np.max([1, int(np.floor(signal_span_factor * len(pspectrum.index)))])
    # obtain the signal frequency bin
    signal_bin = pspectrum["power"][
        span:
    ].idxmax()  # don't count DC signal when searching for the signal bin
    # obtain the harmonics of the signal from the signal bin
    harmonic_bins = [
        pspectrum.index[
            np.abs(pspectrum.index - (mult * signal_bin))
            == np.min(np.abs(pspectrum.index - (mult * signal_bin)))
        ][0]
        for mult in range(1, harmonics + 1)
        if mult * signal_bin <= np.max(freq)
    ]
    # tones that surpass Fs are aliased back to [0, Fs/2] spectrum
    harmonic_bins = [
        pspectrum.index[
            np.abs(pspectrum.index - (fs - bin))
            == np.min(np.abs(pspectrum.index - (fs - bin)))
        ]
        if bin > fs / 2
        else bin
        for bin in harmonic_bins
    ]
    # indexes of the harmonic bins
    harmonic_bins_idxs = [
        pspectrum.index.get_loc(bin) for bin in harmonic_bins if bin in pspectrum.index
    ]
    harmonics_power = np.array(
        [
            np.sum(
                pspectrum["power"]
                .iloc[harmonic_bin_idx - span : harmonic_bin_idx + span]
                .values
            )
            for harmonic_bin_idx in harmonic_bins_idxs
        ]
    )
    # obtain the signal_power
    signal_power = harmonics_power[0]
    SIGNAL_POWER_DB = 10 * np.log10(signal_power)
    signal_dc_power = np.sum(pspectrum["power"].iloc[0 : 0 + span].values)
    DC_POWER_DB = 10 * np.log10(signal_dc_power)
    # ********************************************
    # Computing SFDR - Spurious Free Dynamic Range
    #  - Obtain the power of the
    #       strongest spurious component
    #       of the spectrum (excluding the
    #       DC component) and compute the SFDR.
    # ********************************************
    signal_bin_idx = harmonic_bins_idxs[0]  # get the index of the signal bin
    spurious_spectrum = pspectrum["power"].copy()
    # erase the signal bin from the spurious spectrum
    spurious_spectrum.iloc[signal_bin_idx - span : signal_bin_idx + span] = np.min(
        pspectrum["power"]
    )
    # erase the signal's DC component from the spurious spectrum
    spurious_spectrum.iloc[0 : 0 + span] = np.min(pspectrum["power"])
    # find the strongest spurious component
    spur_bin = spurious_spectrum.idxmax()
    spur_bin_idx = pspectrum.index.get_loc(spur_bin)
    # measure the power of the strongest spurious component
    spur_power = np.sum(
        spurious_spectrum.iloc[spur_bin_idx - span : spur_bin_idx + span].values
    )
    # compute the SFDR
    SFDR = 10 * np.log10(signal_power / spur_power)
    # ********************************************
    # Computing THD - Total Harmonic Distortion
    #  - Obtain the power of each harmonic component
    # ********************************************
    # compute the total power of the sum of the harmonics
    total_distortion_power = np.sum(harmonics_power[1:])
    THD = 10 * np.log10(total_distortion_power / harmonics_power[0])
    # ********************************************
    # Computing SNR - Signal to Noise Ratio
    #  - Obtain the noise power in the spectrum
    # ********************************************

    noise_power = (
        np.sum(pspectrum["power"].values)
        - signal_dc_power
        - signal_power
        - total_distortion_power
    )
    SNR = 10 * np.log10(signal_power / noise_power)
    # ********************************************
    # Computing SNDR - Signal to Noise & Distortion Ratio
    #  - Add the noise and distortion power in
    #     the spectrum and compare them to the
    #     signal power
    # ********************************************
    SNDR = 10 * np.log10(signal_power / (noise_power + total_distortion_power))
    # ********************************************
    # Computing HD2 and HD3 - Fractional Harmonic
    # Distortion of Second and Third order
    # harmonics
    # ********************************************
    HD2 = 10 * np.log10(harmonics_power[1] / harmonics_power[0])
    HD3 = 10 * np.log10(harmonics_power[2] / harmonics_power[0])
    # ********************************************
    # Computing Gain - Output Signal amplitude
    # to Input Signal amplitude ratio
    # ********************************************
    # measure the power of the fundamental harmonic of the input spectrum
    GAIN = np.nan
    GAIN_DB = np.nan
    if bool(input_signal_name):
        if not (input_signal_name in signals.columns):
            raise ValueError(
                f"{input_signal_name} does not belong to the parsed signals."
            )

        vin = np.abs(
            np.fft.fftshift(np.fft.fft(signals[input_signal_name].values) / n_samples)
        )
        freq_in = np.fft.fftshift(np.fft.fftfreq(len(vin), ts))  # [Hz]
        in_power = vin * vin
        in_power_db = np.nan_to_num(
            10 * np.log10(in_power), nan=0.0, posinf=0.0, neginf=0.0, copy=True
        )
        in_spectrum = DataFrame(
            index=freq_in,
            data={"vin": vin, "in_power": in_power, "in_power_db": in_power_db},
        )
        in_pspectrum = in_spectrum[in_spectrum.index >= 0].copy()
        in_signal_bin = in_pspectrum["in_power"][
            0 + span :
        ].idxmax()  # don't count DC signal when searching for the signal bin
        # obtain the harmonics of the signal from the signal bin
        in_harmonic_bins = [
            mult * in_signal_bin
            for mult in range(1, harmonics + 1)
            if mult * signal_bin <= np.max(freq)
        ]
        # tones that surpass Fs are aliased back to [0, Fs/2] spectrum
        in_harmonic_bins = [
            fs - bin if bin > fs / 2 else bin for bin in in_harmonic_bins
        ]
        # indexes of the harmonic bins
        in_harmonic_bins_idxs = [
            pspectrum.index.get_loc(bin) for bin in in_harmonic_bins
        ]
        input_signal_power = np.sum(
            in_pspectrum["in_power"]
            .iloc[in_harmonic_bins_idxs[0] : in_harmonic_bins_idxs[0] + span]
            .values
        )
        GAIN = np.sqrt(signal_power / input_signal_power)
        GAIN_DB = 10 * np.log10(GAIN)
    target_harmonics = list(zip(harmonic_bins, 10 * np.log10(harmonics_power)))
    return (
        spectrum,
        target_harmonics,
        SIGNAL_POWER_DB,
        DC_POWER_DB,
        GAIN,
        GAIN_DB,
        SFDR,
        THD,
        SNR,
        SNDR,
        HD2,
        HD3,
    )


class WaveTypes(Enum):
    """_summary_

    Args:
        PULSE (str): Pure Pulse waveform selector
        SAWTOOTH (str): Pure Sawtooth waveform selector
        DEFAULT (str): Default modulated, square waveform selector
    """

    PULSE = "pulse"
    SAWTOOTH = "sawtooth"
    DEFAULT = "default"


@timer
def daosDynamicEval(
    signals: DataFrame,
    output_signal_name: str,
    input_signal_name: str = None,
    harmonics: int = 7,
    signal_span_factor: float = 0.0,
    noise_power: float = -1.0,
    downsampling: int = 1,
    wave_type: str = "default",
    levels: tuple = (0.1, 0.9),
    show_rise_time_eval: bool = False,
) -> tuple[DataFrame, float, float, float, float, float, float, float, float, float]:
    from heapq import nlargest
    from warnings import warn
    from matplotlib.pyplot import (
        plot,
        show,
        xlabel,
        ylabel,
        grid,
        title,
        legend,
        arrow,
        rc,
        clf,
    )

    """_summary_
    Dynamic performance evaluation of Discrete Analog Output Systems (CAOS)
    Args:
        signals (DataFrame): The time series data with all the correspondant signals.
        harmonics (int, optional): The number of harmonics to be used in the CAOS. Defaults to 7.
        signal_span_factor (float, optional): The factor to be used to scale the signal span. Defaults to 0.0.
        noise_power (float, optional): The noise power to be used in the CAOS. Defaults to -1.0.
        output_signal_name (str): The name of the output signal.
        input_signal_name (str, optional): The name of the input signal. Defaults to None. In no input signal is provided,
        the Gain of the system will not be computed.
        wave_type (str, optional): The type of wave to be used in the DAOS. Defaults to "pulse". Options:
        levels (tuple, optional): The levels to be used in the Risetime computation. Defaults to (0.1, 0.9).
    Returns:
        tuple[DataFrame, float, float, float, float, float, float, float]: The CAOS performance evaluation results.
        DataFrame: The frequency spectrum of the CAOS output signal in volt, volt squared (power in watt) and decibels.
        float(1): Output Signal's power in decibels
        float(2): Output Signal's DC power (in dB)
        float(3): Gain in linear scale
        float(4): Gain in dB
        float(5): Spurious Free Dynamic Range (SFDR) metric
        float(6): Total Harmonic Distortion (THD) metric
        float(7): Signal to Noise Ratio (SNR) metric
        float(8): Signal to Noise & Distortion Ratio (SNNDR) metric
        float(9): Fractional Second-Harmonic Distortion (HD2) metric
        float(10): Fractional Third-Harmonic Distortion (HD3) metric
        float(11): Average Rise Time (ns) in 90% of the signal
        float(12): Estimated Bandwidth (Hz) of the output signal
    """

    if not bool(signals.index.name):
        raise ValueError("The signals DataFrame must have time axis.")
    if not (output_signal_name in signals.columns):
        raise ValueError(f"{output_signal_name} does not belong to the parsed signals.")
    # perform downsampling if so was chosen
    signals = signals[::downsampling]
    ts = signals.index.values[1] - signals.index.values[0]
    fs = 1.0 / ts
    n_samples = len(signals.index)
    if noise_power > 0:
        noise_watt = (10 ** (noise_power / 10)) * 1e-3
        signals[output_signal_name] = signals[output_signal_name] + np.random.normal(
            0, np.sqrt(noise_watt), size=n_samples
        )
    vout = np.abs(
        np.fft.fftshift(np.fft.fft(signals[output_signal_name].values) / n_samples)
    )  # [V]
    freq = np.fft.fftshift(np.fft.fftfreq(len(vout), ts))  # [Hz]
    power = (
        vout * vout
    )  # [V^2] - square the voltage spectrum to obtain the power spectrum
    power_db = 10 * np.log10(power)  # [dB] - convert the power spectrum to dB
    spectrum = DataFrame(
        index=freq, data={"vout": vout, "power": power, "power_db": power_db}
    )
    # positive frequencies spectrum
    pspectrum = spectrum[spectrum.index >= 0].copy()
    # ********************************************
    # Obtaining the ADC's output signal power
    # ********************************************
    # determine the span of the signal's spectrum to consider it's total dispersed power
    span = np.max([1, int(np.floor(signal_span_factor * len(pspectrum.index)))])
    # obtain the signal frequency bin
    signal_bin = pspectrum["power"][
        span:
    ].idxmax()  # don't count DC signal when searching for the signal bin
    # obtain the harmonics of the signal from the signal bin
    harmonic_bins = [
        pspectrum.index[
            np.abs(pspectrum.index - (mult * signal_bin))
            == np.min(np.abs(pspectrum.index - (mult * signal_bin)))
        ][0]
        for mult in range(1, harmonics + 1)
        if mult * signal_bin <= np.max(freq)
    ]
    # tones that surpass Fs are aliased back to [0, Fs/2] spectrum
    harmonic_bins = [
        pspectrum.index[
            np.abs(pspectrum.index - (fs - bin))
            == np.min(np.abs(pspectrum.index - (fs - bin)))
        ]
        if bin > fs / 2
        else bin
        for bin in harmonic_bins
    ]
    # indexes of the harmonic bins
    harmonic_bins_idxs = [pspectrum.index.get_loc(bin) for bin in harmonic_bins]
    harmonics_power = np.array(
        [
            np.sum(
                pspectrum["power"]
                .iloc[harmonic_bin_idx - span : harmonic_bin_idx + span]
                .values
            )
            for harmonic_bin_idx in harmonic_bins_idxs
        ]
    )
    # obtain the signal_power
    signal_power = harmonics_power[0]
    SIGNAL_POWER_DB = 10 * np.log10(signal_power)
    signal_dc_power = np.sum(pspectrum["power"].iloc[0 : 0 + span].values)
    DC_POWER_DB = 10 * np.log10(signal_dc_power)
    # ********************************************
    # Computing SFDR - Spurious Free Dynamic Range
    #  - Obtain the power of the
    #       strongest spurious component
    #       of the spectrum (excluding the
    #       DC component) and compute the SFDR.
    # ********************************************
    signal_bin_idx = harmonic_bins_idxs[0]  # get the index of the signal bin
    spurious_spectrum = pspectrum["power"].copy()
    # erase the signal bin from the spurious spectrum
    spurious_spectrum.iloc[signal_bin_idx - span : signal_bin_idx + span] = np.min(
        pspectrum["power"]
    )
    # erase the signal's DC component from the spurious spectrum
    spurious_spectrum.iloc[0 : 0 + span] = np.min(pspectrum["power"])
    # find the strongest spurious component
    spur_bin = spurious_spectrum.idxmax()
    spur_bin_idx = pspectrum.index.get_loc(spur_bin)
    # measure the power of the strongest spurious component
    spur_power = np.sum(
        spurious_spectrum.iloc[spur_bin_idx - span : spur_bin_idx + span].values
    )
    # compute the SFDR
    SFDR = 10 * np.log10(signal_power / spur_power)
    # ********************************************
    # Computing THD - Total Harmonic Distortion
    #  - Obtain the power of each harmonic component
    # ********************************************
    # compute the total power of the sum of the harmonics
    total_distortion_power = np.sum(harmonics_power[1:])
    THD = 10 * np.log10(total_distortion_power / harmonics_power[0])
    # ********************************************
    # Computing SNR - Signal to Noise Ratio
    #  - Obtain the noise power in the spectrum
    # ********************************************

    noise_power = (
        np.sum(pspectrum["power"].values)
        - signal_dc_power
        - signal_power
        - total_distortion_power
    )
    SNR = 10 * np.log10(signal_power / noise_power)
    # ********************************************
    # Computing SNDR - Signal to Noise & Distortion Ratio
    #  - Add the noise and distortion power in
    #     the spectrum and compare them to the
    #     signal power
    # ********************************************
    SNDR = 10 * np.log10(signal_power / (noise_power + total_distortion_power))
    # ********************************************
    # Computing HD2 and HD3 - Fractional Harmonic
    # Distortion of Second and Third order
    # harmonics
    # ********************************************
    HD2 = np.nan
    HD3 = np.nan
    try:
        HD2 = 10 * np.log10(harmonics_power[1] / harmonics_power[0])
        HD3 = 10 * np.log10(harmonics_power[2] / harmonics_power[0])
    except IndexError:
        log.warning(
            "\nHarmonics of order above the fundamental were not accessible.\nThis is likely because the sampling frequency (Fs) \n is lower than the signal's fundamental frequency."
        )
    # ********************************************
    # Computing Gain - Output Signal amplitude
    # to Input Signal amplitude ratio
    # ********************************************
    # measure the power of the fundamental harmonic of the input spectrum and divide both output and input powers
    GAIN = np.nan
    GAIN_DB = np.nan
    if bool(input_signal_name):
        if not (input_signal_name in signals.columns):
            raise ValueError(
                f"{input_signal_name} does not belong to the parsed signals."
            )

        vin = np.abs(
            np.fft.fftshift(np.fft.fft(signals[input_signal_name].values) / n_samples)
        )
        freq_in = np.fft.fftshift(np.fft.fftfreq(len(vin), ts))  # [Hz]
        in_power = vin * vin
        in_power_db = np.nan_to_num(
            10 * np.log10(in_power), nan=0.0, posinf=0.0, neginf=0.0, copy=True
        )
        in_spectrum = DataFrame(
            index=freq_in,
            data={"vin": vin, "in_power": in_power, "in_power_db": in_power_db},
        )
        in_pspectrum = in_spectrum[in_spectrum.index >= 0].copy()
        in_signal_bin = in_pspectrum["in_power"][
            0 + span :
        ].idxmax()  # don't count DC signal when searching for the signal bin
        # obtain the harmonics of the signal from the signal bin
        in_harmonic_bins = [
            mult * in_signal_bin
            for mult in range(1, harmonics + 1)
            if mult * signal_bin <= np.max(freq)
        ]
        # tones that surpass Fs are aliased back to [0, Fs/2] spectrum
        in_harmonic_bins = [
            fs - bin if bin > fs / 2 else bin for bin in in_harmonic_bins
        ]
        # indexes of the harmonic bins
        in_harmonic_bins_idxs = [
            pspectrum.index.get_loc(bin) for bin in in_harmonic_bins
        ]
        input_signal_power = np.sum(
            in_pspectrum["in_power"]
            .iloc[in_harmonic_bins_idxs[0] : in_harmonic_bins_idxs[0] + span]
            .values
        )
        GAIN = np.sqrt(signal_power / input_signal_power)
        GAIN_DB = 10 * np.log10(GAIN)
    # ********************************************
    # Computing output signal's
    # risetime @90% signal variation
    # between static levels
    # ********************************************

    # ********************************************
    # Computing output signal's
    # falltime @90% signal variation
    # between static levels
    # ********************************************
    RISETIME_90 = 0.0
    vout = signals[output_signal_name].values
    if wave_type in [WaveTypes.SAWTOOTH.value, WaveTypes.PULSE.value]:
        threshold_vout = np.min(vout)
    elif wave_type is WaveTypes.DEFAULT.value:
        threshold_vout = np.mean(vout)
    else:
        raise ValueError(
            f"{wave_type} is not a valid wave type. Possible types are: {[elem.value for elem in WaveTypes]}."
        )
    # comput output signal histogram
    hist, bin_edges = np.histogram(vout)
    hist, bin_edges = hist / sum(hist), np.array(bin_edges)
    # through the histogram, find the discrete signal levels to be accounted for in the risetime
    hist_filtered = hist[bin_edges[:-1] > threshold_vout]
    signal_levels_prob = nlargest(2, hist_filtered)
    signal_levels = (
        bin_edges[:-1][bin_edges[:-1] > threshold_vout][
            hist_filtered == signal_levels_prob[0]
        ],
        bin_edges[:-1][bin_edges[:-1] > threshold_vout][
            hist_filtered == signal_levels_prob[1]
        ],
    )
    # upper_signal_levels = sorted((signal_levels[0][0], signal_levels[1][0]))
    signal_levels = signal_levels[0][0], signal_levels[1][0]
    s0, s100 = sorted(signal_levels)
    # measure all the transitions between these the signal levels found using the mean value of the signal
    delta_v = np.diff(vout)
    if levels[0] > levels[1]:
        raise ValueError(
            f"Rise Time computation levels must be in ascending order, but levels {levels} were given."
        )
    level0 = levels[0]
    level1 = levels[1]
    t10 = (s0 + (s100 - s0) * level0 - vout[:-1]) / delta_v
    idx10 = np.where((t10 > 0) & (t10 < 1))[0]
    t10 = idx10 + t10[idx10]
    t90 = (s0 + (s100 - s0) * level1 - vout[:-1]) / delta_v
    idx90 = np.where((t90 > 0) & (t90 < 1))[0]
    t90 = idx90 + t90[idx90]

    # compute all possible transition times, keep the smallest
    idx = np.unravel_index(np.argmin(np.abs(t90[:, None] - t10)), (len(t90), len(t10)))
    RISETIME_90 = (
        np.abs((t90[idx[0]] - t10[idx[1]])) * ts
    )  # finally, compute the risetime
    BANDWIDTH = 1 / RISETIME_90

    if show_rise_time_eval:
        log.warning(
            "\nRise Time Evaluation plotting is dehactivated due to some problems."
        )
        """
        rc("axes", titlesize=14)  # fontsize of the axes title
        rc("axes", labelsize=12)  # fontsize of the x and y labels
        rc("xtick", labelsize=12)  # fontsize of the tick labels
        rc("ytick", labelsize=12)  # fontsize of the tick labels
        rc("legend", fontsize=11)  # legend fontsize
        rc("font", size=11)  # controls default text sizes
        rc("font", family="serif")  # default serif font
        plot(signals.index, vout, label=output_signal_name)
        xlabel("Time [s]")
        ylabel("Voltage [V]")
        grid()
        title(
            f"Output signal RiseTime[{level0*100:.2f}% - {level1*100:.2f}%] Evaluation"
        )
        x = t10[idx[1]] * ts
        y = s0 + (s100 - s0) * level0
        dx = t90[idx[0]] * ts - x
        dy = s0 + (s100 - s0) * level1 - y
        # plot(t10*ts, [s0 + (s100-s0)*level0]*len(t10), 'go')
        plot(x, [y], "go")
        plot(
            x,
            [y],
            "o",
            mec="g",
            mfc="None",
            ms=10,
            label=f"Signal Level[{level0*100}%]",
        )
        # plot(t90*ts, [s0 + (s100-s0)*level1]*len(t90), 'ro')
        plot(x + dx, [y + dy], "ro")
        plot(
            x + dx,
            [y + dy],
            "o",
            mec="r",
            mfc="None",
            ms=10,
            label=f"Signal Level[{level1*100}%]",
        )
        # double sided arrow
        arrow(
            x,
            y,
            dx,
            dy,
            color="k",
            label=f"RiseTime @ [{level1*100}%] = {RISETIME_90/1e-9:.3f} ns",
            width=ts / 2,
            head_length=0.05,
            head_width=ts * 2,
            length_includes_head=True,
        )
        arrow(
            x + dx,
            y + dy,
            -dx,
            -dy,
            color="k",
            width=ts / 2,
            head_length=0.05,
            head_width=2 * ts,
            length_includes_head=True,
        )
        legend(loc="lower right")
        show()
        clf()
        """
    target_harmonics = list(zip(harmonic_bins, 10 * np.log10(harmonics_power)))
    return (
        spectrum,
        target_harmonics,
        SIGNAL_POWER_DB,
        DC_POWER_DB,
        GAIN,
        GAIN_DB,
        SFDR,
        THD,
        SNR,
        SNDR,
        HD2,
        HD3,
        RISETIME_90,
        BANDWIDTH,
    )
