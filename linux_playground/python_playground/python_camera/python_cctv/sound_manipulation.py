from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from scipy.io.wavfile import write
from scipy.io import wavfile
import vlc
from enum import Enum, auto
from matplotlib import pyplot as plt
import plotly.graph_objs as go

class PLOT_TYPES(Enum):
    """
    There's 2 types of plotting, One is MATPLOTLIB and another is PLOTLY
    :cvar MATPLOTLIB: is old and trusty-worth plot library for simple DSP and so on...
    :cvar PLOTLY: is more advance and futuristic
    """
    MATPLOTLIB = auto()
    PLOTLY = auto()
    KAKI = auto()
    GADOL = auto()
    MEOD = auto()


def wave_creator(power: float = 0.5, sample_rate: int = 44100, duration: int = 2, frequency: int = 400, norm: bool = False, sound_file_name: str = "tone.wav") -> tuple[np.ndarray, np.ndarray]:
    """
    creating wave sound with amplitude sinus math
    saving it in wav-sound-file.
    :param sample_rate: 
    :param duration:
    :param frequency:
    :param sound_file_name:
    :return: return the samples X and Y sinus wave.
    """
    t = np.linspace(0, duration, sample_rate * duration)
    wave = power * np.sin(2 * np.pi * frequency * t)

    if norm:
        # PCM16
        wave = wave / np.max(np.abs(wave)) # normalization
        wave = np.int16(wave * 32767) # make it pcm16
    wavfile.write(sound_file_name, sample_rate, wave) # writes pcm16




    # write(sound_file_name, sample_rate, wave.astype(np.float32))
    return t, wave


def read_wav_file(sound_filename: str = "tone.wave") -> tuple[Any, Any]:
    rate, data = wavfile.read(sound_filename)
    return rate, data


def play_blocking(sound_file_name: str = "tone.wav") -> None:
    import vlc, time
    player = vlc.MediaPlayer(sound_file_name)
    player.play()
    while True:
        state = player.get_state()
        if state in [vlc.State.Ended, vlc.State.Error]:
            break
        time.sleep(0.1)


def plot_creator(plot_library: PLOT_TYPES = PLOT_TYPES.MATPLOTLIB, sound_file_name: str = "tone.wav"):
    time, wave = wave_creator(power=0.5, duration=5, frequency=432, sound_file_name=sound_file_name, norm=True)
    if plot_library == PLOT_TYPES.MATPLOTLIB:
        # pass
        plot_out = MatplotlibSoundGraph(time, wave)
        plot_out.waveform_creator()
        

    elif plot_library == PLOT_TYPES.PLOTLY:
        # raise NotImplementedError(f"{plot_library} is not implemented yet")
        plot_out = PlotlySoundGraph(time, wave)
        plot_out.waveform_creator()
    
    play_blocking(sound_file_name=sound_file_name)
    sample_rate, data = read_wav_file(sound_filename=sound_file_name)
    pass
    


def diff_playback():
    for i in range(10, 800):
        time, wave = wave_creator(power=1000, duration=1, frequency=i, sound_file_name="tone.wav", norm=True)
        play_blocking(sound_file_name="tone.wav")
        print(f"{i}")
        # time.sleep(1)


class DPSShowGraph(ABC):
    def __init__(self, time, wave):
        self.time = time
        self.wave = wave
    
    @abstractmethod
    def waveform_creator(self):
        pass

    @abstractmethod
    def fft_creator(self):
        pass


class MatplotlibSoundGraph(DPSShowGraph):
    def waveform_creator(self):
        # plt.figure(figsize=(10,4))
        plt.plot(self.time[:10000], self.wave[:10000])
        plt.savefig('waveform.png')


    def fft_creator(self):
        pass    


class PlotlySoundGraph(DPSShowGraph):
    def waveform_creator(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.time, y=self.wave, mode='lines', name='sine wave Hz'))

        fig.update_layout(
            title='Waveform Hz',
            xaxis_title='Time [s]',
            yaxis_title='Amplitude',
        )

        fig.write_html('plot.html')


    def fft_creator(self):
        pass






if __name__ == "__main__":
    # plot_creator(plot_library=PLOT_TYPES.PLOTLY)
    plot_creator(plot_library=PLOT_TYPES.PLOTLY, sound_file_name="tone.wav")
    # diff_playback()