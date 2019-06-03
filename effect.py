import hyperion
import time
import colorsys
import math
import pyaudio
import numpy as np
from numpy import inf

RATE = 44100
BUFFER = 882

BANDS = hyperion.ledCount / 2
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

""" Define some variables """
sleepTime = 0.5
rgb1 = [0, 255, 100]
cycle = 0

""" The effect loop """
while not hyperion.abort():
    """ The algorithm to calculate the change in color """
    led_data = bytearray()

    try:
        data = np.fft.rfft(np.fromstring(
            stream.read(BUFFER), dtype=np.float32)
        )
    except IOError:
        pass

    data = np.log10(np.sqrt(
        np.real(data)**2+np.imag(data)**2) / BUFFER) * 10

    # print data

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

    # print BAND_DATA

    middle_offset = math.floor(hyperion.horizontal / 2)
    for i in range(hyperion.ledCount):
        # first_led_offset from top left
        # default is clockwise
        index = i
        if not hyperion.clockwise_direction and index != 0:
            index = hyperion.ledCount - index
        
        if hyperion.first_led_offset != 0:
            mult = 1 if hyperion.clockwise_direction else -1
            index = (index + (mult * hyperion.first_led_offset)) % hyperion.ledCount

        index = int((index - middle_offset) % BANDS)
        if i > hyperion.ledCount - hyperion.first_led_offset - middle_offset and i < hyperion.ledCount - middle_offset:
            index = BANDS - index - 1

        # print index

        brightness = BAND_DATA[BANDS - 1 - index] / 256.0
        # brightness = (float(index) / (hyperion.ledCount - 1))
        r = int(max(0, min(rgb1[0] * brightness, 255)))
        g = int(max(0, min(rgb1[1] * brightness, 255)))
        b = int(max(0, min(rgb1[2] * brightness, 255)))

        # print r, g, b, brightness
        

        # if index == 0:
        #     r = 255
        #     g = 0
        #     b = 0

        # if index == hyperion.ledCount - 1:
        # if index == BANDS - 1:
        #     r = 0
        #     g = 0
        #     b = 255
        
        led_data += bytearray((r, g, b))

    """ send the data to hyperion """
    hyperion.setColor(led_data)

    cycle += 0.07

    """ sleep for a while """
    # time.sleep(sleepTime)