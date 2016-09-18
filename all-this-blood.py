#!/usr/bin/env python

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain

import time
import os
import RPi.GPIO as GPIO
from datetime import datetime

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)


def readadc(adcnum, clockpin, mosipin, misopin, cspin):
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

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

GPIO.setwarnings(False)
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

pulse_adc = 0
pulse = False


rate = [0] * 10
lastBeatTime = datetime.now()  # used to find IBI
P = 512  # used to find peak in pulse wave, seeded
T = 512  # used to find trough in pulse wave, seeded
thresh = 525  # used to find instant moment of heart beat, seeded
amp = 100  # used to hold amplitude of pulse waveform, seeded
firstBeat = True  # used to seed rate array so we startup with reasonable BPM
secondBeat = False  # used to seed rate array so we startup with reasonable BPM
IBI = 600
BPM = 0
while True:
    # read the analog pin
    signal = readadc(pulse_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)

    # draw the equivalent number of points in an attempt to draw a vertical
    # pulse sensing graph
   # for i in range(signal / 100):
    #    print ".",

    now = datetime.now()

    # monitor the time since the last beat to avoid noise
    N = (now - lastBeatTime).total_seconds() * 1000

    # avoid dichrotic noise by waiting 3 / 5 of last IBI
    if signal < thresh and N > (IBI / 5) * 3:
        if signal < T:  # T is the trough
            T = signal  # keep track of lowest point in pulse wave

    if signal > thresh and signal > P:  # thresh condition helps avoid noise
        P = signal  # P is the peak
        # keep track of highest point in pulse wave

    # NOW IT'S TIME TO LOOK FOR THE HEART BEAT
    # signal surges up in value every time there is a pulse
    if N > 250:  # avoid high frequency noise
        if signal > thresh and pulse == False and (N > (IBI / 5) * 3):
            pulse = True  # set the pulse flag when we think there is a pulse
            IBI = N  # measure time between beats in mS
            lastBeatTime = now  # keep track of time for next pulse

            if secondBeat:  # if this is the second beat, if secondBeat == TRUE
                secondBeat = False  # clear secondBeat flag
                for i in range(0, 10):  # seed the running total to get a realisitic BPM at startup
                    rate[i] = IBI

            if firstBeat:  # if it's the first time we found a beat, if firstBeat == TRUE
                firstBeat = False  # clear firstBeat flag
                secondBeat = True  # set the second beat flag
                time.sleep(0.002)
                continue  # IBI value is unreliable so discard it

            # keep a running total of the last 10 IBI values
            runningTotal = 0  # clear the runningTotal variable

            for i in range(0, 9):  # shift data in the rate array
                rate[i] = rate[i + 1]  # and drop the oldest IBI value
                runningTotal += rate[i]  # add up the 9 oldest IBI values

            rate[9] = IBI  # add the latest IBI to the rate array
            runningTotal += rate[9]  # add the latest IBI to runningTotal
            runningTotal /= 10  # average the last 10 IBI values
            BPM = 60000 / runningTotal  # how many beats can fit into a minute? that's BPM!
            QS = True  # set Quantified Self flag

    if signal < thresh and pulse == True:  # when the values are going down, the beat is over
        pulse = False  # reset the pulse flag so we can do it again
        amp = P - T  # get amplitude of the pulse wave
        thresh = amp / 2 + T  # set thresh at 50 % of the amplitude
        P = thresh  # reset these for next time
        T = thresh
        print "Beat %s" % BPM

    if N > 2500:  # if 2.5 seconds go by without a beat
        thresh = 512  # set thresh default
        P = 512  # set P default
        T = 512  # set T default
        lastBeatTime = now  # bring the lastBeatTime up to date
        firstBeat = True  # set these to avoid noise
        secondBeat = False  # when we get the heartbeat back
   # print ""
    time.sleep(0.002)
