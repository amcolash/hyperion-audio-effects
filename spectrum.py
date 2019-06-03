#!/usr/bin/env python
# -*- charset utf8 -*-

# inital code from: https://gist.github.com/netom/8221b3588158021704d5891a4f9c0edd

import pyaudio
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation

RATE = 44100
BUFFER = 882

BANDS = 24
BAND_DATA = np.zeros(BANDS)

p = pyaudio.PyAudio()

stream = p.open(
    format = pyaudio.paFloat32,
    channels = 1,
    rate = RATE,
    input = True,
    output = False,
    frames_per_buffer = BUFFER
)

fig = plt.figure()
plt.subplot(211)
line1 = plt.plot([],[])[0]
plt.xlim(0, RATE/2+1)
plt.ylim(-60, 0)
# plt.xlabel('Frequency')
plt.ylabel('dB')
# plt.title('Spectrometer')
plt.grid()

plt.subplot(212)
line2 = plt.plot([],[], '-ro')[0]
plt.xlim(0, BANDS - 1)
plt.ylim(0, 256)
plt.grid()

r = range(0,int(RATE/2+1),int(RATE/BUFFER))
l = len(r)

def init_line():
        line1.set_data(r, [-1000]*l)
        line2.set_data(r, [-1000]*l)
        return (line1,line2,)

def update_line(i):
    try:
        data = np.fft.rfft(np.fromstring(
            stream.read(BUFFER), dtype=np.float32)
        )
    except IOError:
        pass
    data = np.log10(np.sqrt(
        np.real(data)**2+np.imag(data)**2) / BUFFER) * 10
    line1.set_data(r, data)
    
    size = len(data)
    band_size = int(math.floor(size / BANDS))
    new_bands = np.zeros(BANDS)
    count = np.zeros(BANDS)
    for i in range(size):
      band = int(math.floor(float(i) / (band_size + 1)))
      # print i, band
      new_bands[band] += abs(data[i])
      count[band] += 1

    # print count

    # smooth out the last point
    if count[BANDS - 1] < band_size:
      new_bands[BANDS - 1] *= (band_size / count[BANDS - 1] * 1.06)

    # print new_bands, count, size

    for i in range(BANDS):
      new_bands[i] = (50 - ((new_bands[i] / band_size ))) * 7

      if BAND_DATA[i] != float('inf') and BAND_DATA[i] != float('-inf'):
        BAND_DATA[i] = BAND_DATA[i] * 0.9 + new_bands[i] * 0.1
      else:
        BAND_DATA[i] = new_bands[i]

      BAND_DATA[i] = max(0, BAND_DATA[i])

    line2.set_data(np.arange(0, BANDS), BAND_DATA)
    # print BAND_DATA

    return (line1,line2,)

line_ani = matplotlib.animation.FuncAnimation(
    fig, update_line, init_func=init_line, interval=25, blit=True
)

plt.show()