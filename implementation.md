# Architecture

Each device is a Raspberry Pi Model A with a USB Bluetooth 4.0 adapter, paired to a bluetooth earpiece for audio recording and playback. 

Slave devices connect to a master device using the 'PAN' bluetooth networking profile, providing a shared IP networking layer. Each master network adapter hosts a broker on the standard MQTT port allowing the asynchronous dispatch to subscribers of string and byte array messages published against 'topics' which indicate local events.

This infrastructure enables a set of generic services and statuses to be coordinated together. Devices run python scripts which embody particular regimes for using the infrastructure. The different regimes match to the different designs offered by delegates to our co-design workshops.

This architecture not only provides a basis for implementing the regimes, but also for making eventing within the infrastructure visible, able to be monitored and discussed as part of the co-design approach. They loosely correspond to the broadcast blocks used in our Scratch behaviour authoring.

## Services

Services are a combination of local operations on a device, (such as monitoring a button, or playing audio files) with an MQTT subscription and publishing strategy. They use an MQTT topic namespace to define their activities. Clients and Servers for each service are implemented.

#### Topics 

* button/#
	- numerically indexed or named buttons
	- messages dispatched; pushed, released
* light/#
	- numerically indexed or named lights
	- messages handled; CSS color names and specifications
* track/#
	- tracks named by their MD5 hash plus file extension
	- messages handled; play,pause,rewind,delete
* recorder/#
	- numerically indexed or named audio inputs
	- messages handled; record,pause,close
* player/#
	- numerically indexed or named playback slots, wired to audio outputs
	- messages handled; load:[blob name], play, pause, rewind, eject
* blob/#
	- [binary large objects] file contents sent against their name
	- messages handled; byte array payloads synchronized to a local folder

## Application Logic



## Unit testing

Unit testing uses the 'trial' unit testing framework provided as part of python's [Twisted framework](http://twistedmatrix.com), which enables asynchronous client-server interactions to be triggered and validated.

