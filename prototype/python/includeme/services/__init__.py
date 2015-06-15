from paho import mqtt

import pymedia.audio.sound as sound
import pymedia.audio.acodec as acodec

defaultDir = "./"
mqttHost, mqttPort, mqttTimeout = ("localhost", 1883, 5)
defaultBrokerConfig = (mqttHost, mqttPort, mqttTimeout)

def publish_file(mqttClient,fileRef):
    mqttClient.publish("folder/default/" + fileRef.name, fileRef.read())

# Attaches to a local mqtt broker and subscribes to a
# specific topic pattern
class Adaptor(object):
    def __init__(self, topic, brokerConfig=defaultBrokerConfig):
        self.topic = topic
        
        client = mqtt.Client()
        client.connect(*brokerConfig)
        client.on_message = self.handle_message
        client.subscribe(topic)
        client.loop_start()
        self.client = client
        
    def handle_message(self, client, userdata, msg):
        pass
    
    # shuts down the mqtt client and handler thread
    def dispose(self):
        client = self.client
        self.client = None
        client.disconnect()
        Thread(client.loop_stop).start() # needed to avoid thread join issue

# Subscribes to a topic, and has a mapping between
# regular expressions (RegEx) which match MQTT messages and
# callable handlers. It extracts string arguments
# for the callables using RegEx subgroups where they exist
class RoutingAdaptor(Adaptor):
    def __init__(self, topic, lookup):
        super(Adapter,self).__init__(topic)
        self.lookup = lookup
    
    def handle_message(self, client, userdata, msg):
        for pattern,function in self.lookup.iteritems():
            match = re.search(pattern,msg.payload)
            if(match):
                groups = match.groups()
                if groups == None:
                    groups = ()
                return function(*groups)


class AbstractRecorder(RoutingAdaptor):
    def __init__(self, name="default"):
        super(RoutingAdaptor,self).__init__("recorder/" + self.name, {
            "record":self.record,
            "pause" :self.pause,
            "stop"  :self.stop,
        })
        self.status = "idle"

    def record(self):
        if self.status == "idle":
            self.status = "record"
            Thread(target=self.writeloop).start()
        else:
            raise Error("Not idle, can't record")
        
    def pause(self):
        if self.status == "record":
            self.status = "pause"
        else:
            raise Error("Not recording, can't pause")

    def resume(self):
        if self.status == "pause":
            self.status = "record"
        else:
            raise Error("Not paused, can't resume")
 
    def stop(self):
        self.status = "stop"

    def writeloop(self):
        raise Error("writeloop in AbstractRecorder not yet implemented")
    


class PymediaRecorder(AbstractRecorder):
    
    def writeloop(self):
        self.file = open(defaultDir + self.name + '.tmp', 'wb' )
        self.ac= acodec.Encoder({
            'id': acodec.getCodecId( 'mp3' ),
            'bitrate': 64000,
            'sample_rate': 22050,
            'channels': 2
        })
        self.sound= sound.Input( 22050, 2, sound.AFMT_S16_LE )
        self.sound.start()
        while self.status!="stop" and sound.getPosition() <= MAX_SECONDS:
            soundbytes=self.sound.getData()
            if self.status == "record":
                if soundbytes and len(soundbytes) :
                    for frame in self.ac.encode( s ):
                      self.file.write( frame )
                else:
                  time.sleep( .003 )      
        self.sound.stop()
        self.file.close()
        publish_file(self.client, self.file)
        self.status = "idle"

def main():

    # launch the recorder service
    recorder = PymediaRecorder()

    # monitor for a new file
    fileclient = mqtt.Client()
    fileclient.loop_start()
    fileclient.connect(*defaultBrokerConfig)
    def handle_message(client, userdata, msg):
        print "Received " + msg.topic
        print "Payload size:" + len(msg.payload)
    fileclient.subscribe("file/#")
    fileclient.on_message = handle_message
    fileclient.loop_start()

    # trigger a recording
    recorderclient = mqtt.Client()
    recorderclient.loop_start()
    recorderclient.connect(*defaultBrokerConfig)
    recorderclient.publish(recorder.topic,"record")
    sleep(1)
    recorderclient.publish(recorder.topic,"pause")
    sleep(1)
    recorderclient.publish(recorder.topic,"resume")
    sleep(1)
    recorderclient.publish(recorder.topic,"stop")
    sleep(1)
    
    recorderclient.loop_stop()
    recorderclient.disconnect()
    fileclient.loop_stop()
    fileclient.disconnect()

    recorder.dispose()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()