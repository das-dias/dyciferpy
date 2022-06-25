## Dynamic Performance Indicators

This document presents simple and straightforward mathematical descriptions of the perfromance indicators that ```DYCIFER``` is, as of now, able to compute.

Considering a simple sinusoidal voltage signal $s(t)$ with a superposed Gaussian white-noise signal $n(t)$ with an average amplitude $\mu_{n} = 0.0$ (V):

$s(t)=A_{S}cos(\omega _S t + \phi) + S_{DC} + n(t)$ (V)

### 1 - Signal Strength $P_S$

The measured power of a signal, given by the squared value of it's amplitude.

- $P_S = 10.log_{10}(A_{S}^2)$ (dB)

### 2 - DC Signal Strength $P_{DC}$

The measured power of the *direct current* (DC) signal superposed to signal $s(t)$

- $P_{DC}=10.log_{10}(S_{DC})$ (dB)
  
### 3 - Gain

Considering a second voltage signal serving as input to a system that outputs $s(t)$:

$v(t)=A_{V}cos(\omega _V t + \phi _V) + V_{DC}$ (V)

Then the gain of such a system can be defined as the power ratio between the output and input signal:

- $G = \frac{A_S^2}{A_V^2}$ ($W.W^{-1}$)

The gain expressed in decibels is given by:
- $G_{dB} = 10.log_{10}(G)$ (dB)

The voltage gain of the same system can therefore be given by:
- $G_{Voltage} = \frac{A_S}{A_V}$ ($V.V^{-1}$)

And thus, its decibels representation be given by:

- $G_{dB - Voltage}=20.log_{10}(G_{Voltage})$ (dB)

### 4 - 2<sup>nd</sup> Order Harmonic Distortion (HD2)

### 5 - 3<sup>rd</sup> Order Harmonic Distortion (HD3)

### 6 - Total Harmonic Distortion (THD)