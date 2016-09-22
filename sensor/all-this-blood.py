#!/usr/bin/env python
# Simple websocket server that emits 
#
# M3008 reading logic from Adafruit
# --------
# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain
# --------
# .
# Heartbeat logic ported  from Pulse sensor: https://github.com/WorldFamousElectronics/PulseSensor_Amped_Arduino
#
import sys
import time
import asyncio
import os
import json
import websockets
import netifaces
import RPi.GPIO as GPIO
from datetime import datetime

EPOCH = datetime.utcfromtimestamp(0)

SAMPLE_INTERVAL = 0.002 # sec

WEBSOCKET_PORT = 5678 

# GPIO config
pulse_adc = 0
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25


def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    """Read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)"""
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)     # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3    # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1       # first bit is 'null' so drop it
    return adcout

class IfIOnly():
    """Samples heartbeat sensor and tracks state of heartbeat sampling"""
    def __init__(self):
        self.pulse = False
        self.rate = [0] * 10
        self.lastBeatTime = datetime.now()  # used to find IBI
        self.P = 512  # used to find peak in pulse wave, seeded
        self.T = 512  # used to find trough in pulse wave, seeded
        self.thresh = 525  # used to find instant moment of heart beat, seeded
        self.amp = 100  # used to hold amplitude of pulse waveform, seeded
        self.firstBeat = True  # used to seed rate array so we startup with reasonable BPM
        self.secondBeat = False  # used to seed rate array so we startup with reasonable BPM
        self.IBI = 600
        self.BPM = 0

    def _sample(self):
        return readadc(pulse_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)

    def beat(self):
        """Sample from sensor and update internal state"""
        should_return = False
        signal = self._sample()

        # monitor the time since the last beat to avoid noise
        now = datetime.now()
        self.N = (now - self.lastBeatTime).total_seconds() * 1000

        # avoid dichrotic noise by waiting 3 / 5 of last IBI
        if signal < self.thresh and self.N > (self.IBI / 5) * 3:
            if signal < self.T:  # T is the trough
                self.T = signal  # keep track of lowest point in pulse wave

        if signal > self.thresh and signal > self.P:  # thresh condition helps avoid noise
            self.P = signal  # P is the peak
            # keep track of highest point in pulse wave

        # NOW IT'S TIME TO LOOK FOR THE HEART BEAT
        # signal surges up in value every time there is a pulse
        if self.N > 250:  # avoid high frequency noise
            if signal > self.thresh and self.pulse == False and (self.N > (self.IBI / 5) * 3):
                self.pulse = True  # set the pulse flag when we think there is a pulse
                self.IBI = self.N  # measure time between beats in mS
                self.lastBeatTime = now  # keep track of time for next pulse

                if self.secondBeat:  # if this is the second beat, if secondBeat == TRUE
                    self.secondBeat = False  # clear secondBeat flag
                    for i in range(0, 10):  # seed the running total to get a realisitic BPM at startup
                        self.rate[i] = self.IBI

                if self.firstBeat:  # if it's the first time we found a beat, if firstBeat == TRUE
                    self.firstBeat = False  # clear firstBeat flag
                    self.secondBeat = True  # set the second beat flag
                    return None  # IBI value is unreliable so discard it

                # keep a running total of the last 10 IBI values
                runningTotal = 0  # clear the runningTotal variable

                for i in range(0, 9):  # shift data in the rate array
                    self.rate[i] = self.rate[i + 1]  # and drop the oldest IBI value
                    runningTotal += self.rate[i]  # add up the 9 oldest IBI values

                self.rate[9] = self.IBI  # add the latest IBI to the rate array
                runningTotal += self.rate[9]  # add the latest IBI to runningTotal
                runningTotal /= 10  # average the last 10 IBI values
                self.BPM = 60000 / runningTotal  # how many beats can fit into a minute? that's BPM!
                self.QS = True  # set Quantified Self flag
                should_return = True

        if signal < self.thresh and self.pulse == True:  # when the values are going down, the beat is over
            self.pulse = False  # reset the pulse flag so we can do it again
            self.amp = self.P - self.T  # get amplitude of the pulse wave
            self.thresh = self.amp / 2 + self.T  # set thresh at 50 % of the amplitude
            self.P = self.thresh  # reset these for next time
            self.T = self.thresh

        if self.N > 2500:  # if 2.5 seconds go by without a beat
            self.thresh = 512  # set thresh default
            self.P = 512  # set P default
            self.T = 512  # set T default
            self.lastBeatTime = now  # bring the lastBeatTime up to date
            self.firstBeat = True  # set these to avoid noise
            self.secondBeat = False  # when we get the heartbeat back

        if should_return:
            return {
                'bpm': self.BPM,
                'time': int((now - EPOCH).total_seconds() * 1000.0),
                'delta': self.N
            }

async def life(websocket, path):
    """Websocket handler"""
    heart = IfIOnly()
    try:
        while True:
            result = heart.beat()
            if result:
                print("Beat {0}".format(result['bpm']))
                await websocket.send(json.dumps(result))
            await asyncio.sleep(SAMPLE_INTERVAL)
    finally:
        await websocket.close()


if __name__ == '__main__':
    # Config GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)

    loop = asyncio.get_event_loop()
    for interface in sys.argv[1:]:
        ip = netifaces.ifaddresses(interface)[2][0]['addr']
        start_server = websockets.serve(life, ip, WEBSOCKET_PORT)
        loop.run_until_complete(start_server)

    loop.run_forever()

