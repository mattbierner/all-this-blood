<div align="center">
    <h1>I Don't Know How We Can See Each Other Through All This Blood</h1>
    <i>he said in his most goth voice</i>
</div>

This repo contains the source code used in [my project using a heartbeat sensor to modify my vision][post]. Check out the post more details on the experiment

## Sensor
This Python script collects heartbeat data from a [Pulse Sensor][pulse], sending heartbeat events over a websocket to the VR headset. It targets a Raspberry Pi that is using a MCP3008 analog to digital converter for the Pulse Sensor.

The code requires Python 3.5+, and the [RPi.GPIO](https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008) and [webksockets](https://pypi.python.org/pypi/websockets) libraries.

To start it, simply run:

```bash
$ python3 sensor/all-this-blood.py eth0
```

The script arguments specify which network devices to serve the websocket on.


## Site
The website is designed to be run on an iPhone used with Google Cardboard. It takes the mjpeg stream from the camera and the heartbeat events, and uses WebGL to modify your vision in realtime.

The site uses webpack. To run it:

```bash
$ cd viewer
$ npm install

# Edit `src/config.js` to provide the expected ip address of the Raspberry pi
# and rebuild
$ webpack

# server up index.html somehow
$ http-server index.html
```

## Credits

* [Beartbeat ping sound](http://freesound.org/people/Benboncan/sounds/63832/)
* [adafruit mcp3008 Python code](http://threejs.org/docs/index.html#Manual/Introduction/Creating_a_scene)
* [Pulse sensor Arduino sample code](https://github.com/WorldFamousElectronics/PulseSensor_Amped_Arduino) 
* [Three.js](http://freesound.org/people/Benboncan/sounds/63832/)



[pulse]: http://pulsesensor.com/

[post]: http://blog.mattbierner.com/all-this-blood