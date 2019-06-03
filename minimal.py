import pyaudio
import numpy as np
import math
import time
from numpy import inf

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

while True:
  try:
    data = np.fft.rfft(np.fromstring(
      stream.read(BUFFER, exception_on_overflow=False), dtype=np.float32)
    )
  except IOError:
    pass
  
  data = np.log10(np.sqrt(
    np.real(data)**2+np.imag(data)**2) / BUFFER) * 10
    
  size = len(data)
  band_size = int(math.floor(size / BANDS))
  new_bands = np.zeros(BANDS)
  count = np.zeros(BANDS)
  for i in range(size):
    band = int(math.floor(float(i) / (band_size + 1)))
    # print i, band
    new_bands[band] += abs(data[i])
    count[band] += 1

  # smooth out the last point
  if count[BANDS - 1] < band_size:
    new_bands[BANDS - 1] *= (band_size / count[BANDS - 1] * 1.06)

  # print new_bands, count, size

  for i in range(BANDS):
    new_bands[i] = (50 - ((new_bands[i] / band_size ))) * 7
    if (new_bands[i] == inf):
        new_bands[i] = 256
    if (new_bands[i] == -inf):
        new_bands[i] = 0

    BAND_DATA[i] = BAND_DATA[i] * 0.9 + new_bands[i] * 0.1
    BAND_DATA[i] = min(max(0, BAND_DATA[i]), 256)

  print BAND_DATA