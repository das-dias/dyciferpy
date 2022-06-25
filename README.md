![GitHub Workflow Status](https://img.shields.io/github/workflow/status/das-dias/dyciferpy/dycifer)
![GitHub](https://img.shields.io/github/license/das-dias/dyciferpy)
![GitHub issues](https://img.shields.io/github/issues/das-dias/dyciferpy)
![GitHub package.json version (branch)](https://img.shields.io/github/package-json/v/das-dias/dyciferpy/master)
![GitHub last commit](https://img.shields.io/github/last-commit/das-dias/dyciferpy)

![banner](./docs/imgs/DYCIFER2.png)

``` Dynamic Circuit Performance Evaluation Tool (DYCIFER) ```

 is a tool written in ```Python``` that allows for the extraction of the Performance Indicators of Dynamic Integrated Circuits. Through the analysis of each system's signals (both input and output), the tool will be able to extract indicators such as the *Total Harmonic Distortion* (THD) or *Signal to Noise & Distortion Ratio* (SNDR) of dynamic integrated circuit.

## How does it work
Any integrated circuit designer can simulate the time response of an implemented system through a *Transient Analysis*, which is a basic concept of Electric Circuits Theory. The exported data to Comma Separated Values files (.CSV) can be parsed as input to the tool.
In the examples provided, ®Cadence Virtuoso's time response simulator was used to obtain some of the time response data.

![fft-algo](./docs/imgs/fft-algo-inverted.png)

From the simulated time response data of the system we want to analyze, the [*Fast Fourier Transform* (FFT)](URL "brilliant.org/wiki/discrete-fourier-transform/") (core) algorithm is used to enable the extraction of all the *Dynamic Circuit Performance Indicators* listed in the table below. From these indicators, an integrated circuit designer can eccurately measure the performance of the designed system.

| Performance Indicator | Description |
| --- | --- |
| [Signal Strength](./docs/indicators.md) | Power of the analysed signal |
| [DC Signal Strength](./docs/indicators.md) | Power of the DC component of the analysed signal |
| [ENOB](./docs/enob.md) | Effective Number of Bits |
| [SFDR](./docs/indicators.md) | Spurious Free Dynamic Range |
| [SNR](./docs/indicators.md) | Signal to Noise Ratio |
| [THD](./docs/indicators.md) | Total Harmonic Distortion |
| [SNDR](./docs/indicators.md) | Signal to Noise & Distortion Ratio |
| [HD2](./docs/indicators.md) | 2nd Order Harmonic Distortion Ratio |
| [HD3](./docs/indicators.md) | 3rd Order Harmonic Distortion Ratio |
| [Gain](./docs/indicators.md) | Power Ratio between the Output and Input signals |
| [Rise Time [90%]](./docs/rise-time.md) | The total time it takes the signal to rise from 10% up to 90% of its total amplitude - only important in pulse responses or pulse modulated signals. |
| | |

## Dependencies

- [Poetry](URL "https://python-poetry.org/docs/") - ```Poetry``` is the default ®Python package manager, and it allows to easily deploy and install any project or package written in Python language.

Other [package dependencies](./docs/dependencies.md)

## Installation 

It is highly recommended to use ```Poetry``` in order to install ```DYCIFER``` because it will automatically setup the virtual environment and package dependencies necessary to run this tool. \
First of all, ```git-clone``` this repository into a directory:

![git-clone](./docs/imgs/carbon-gitclone.png)
```
git clone https://github.com/das-dias/dyciferpy.git
```

Alternatively, you can [download](URL "https://github.com/das-dias/dyciferpy/archive/refs/heads/master.zip") this repo's ```.zip``` file and extract it into a personal directory, if you don't have [git](URL "https://git-scm.com/book/en/v2/Getting-Started-Installing-Git") installed in your machine.

Next, using ```Poetry```, inside the downloaded repository directory, run the installation command:

![poetry-install](.docs/../docs/imgs/carbon-poetryinstall.png)
```
poetry install
```
## Usage
### Asking for help

```
poetry run dycifer | -h | --help
```

![General Help](.docs/../docs/imgs/general-help.gif)

```DYCIFER``` is a tool designed to run on the console, and as such it features a neat-looking *Command Line Interface* (CLI) that allows for an easy interaction with its sub-frameworks:

- Mixed-signals Integrated Circuits dedicated framework
- Analog Integrated Circuits dedicated framework

### Mixed Signals Integrated Circuit Performance Analysis

```
poetry run dycifer mixedsignals | -h | --help
```

![Mixed-Signals Help](.docs/../docs/imgs/mixedsignals-help.gif)

This sub-framework is mainly dedicated to provide automated performance analysis to the following systems:

- Analog-to-Digital Converters (ADC) (considering parallel output bit lines)
- Digital-to-Analog Converters (DAC) <span style="color:red"> (NOT IMPLEMENTED YET) </span>
- $\Sigma \Delta$ (Sigma-Delta) ADC (considering serial [*Pulse Width Modulated*](URL "https://en.wikipedia.org/wiki/Pulse-width_modulation") output signal line) <span style="color:red"> (NOT IMPLEMENTED YET) </span>
- $\Sigma \Delta$ DAC <span style="color:red"> (NOT IMPLEMENTED YET) </span>
  
### Analog Integrated Circuit Performance Analysis

```
poetry run dycifer analog | -h | --help
```

![Analog Help](.docs/../docs/imgs/analog-help.gif)

This sub-framework provides coverage to two classes of analog integrated systems:

- Continuous Amplitude Output Systems (CAOS)
- Discrete Amplitude Output Systems (DAOS)

The discrimination of analog systems in these two classes provide for powerful, simplified methods to retrieve the performance indicators of (e.g.)

- Transient responses resembling square (or pulse) waves, or pulse modulated sinusoidal waves, regarding DAOS systems

- Sinusoidal waves (impure/distorted/noisy or pure), regarding CAOS systems

## Examples

Detailed examples on the usage of this tool can be found in the following documents:

**Performance Analysis**
- [ADC Performance Analysis](./docs/adc-example.md)
- [CAOS Amplifier Performance Analysis](./docs/amplifier-example.md)
- [DAOS Amplifier Performance Analysis](./docs/daos-amplifier.md)
  
**Saving Images and Performance Indicators**
- [Saving Tables](./docs/saving-tables.md)
- [Saving Images](./docs/saving-images.md)