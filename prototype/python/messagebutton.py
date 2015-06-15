import sys,re

from functools import partial

from paho.mqtt.client import Client

from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QPushButton,QLabel

class Sender(QWidget):
    def __init__(self, numButtons, numLights):
        super(Sender, self).__init__()
        self.buttons = []
        self.lights = []
        self.initMqtt()
        self.initQt(numButtons,numLights)
        
                
    def initMqtt(self):
        self.client = Client()
        self.client.on_connect = self.handle_connect
        self.client.on_message = self.handle_message
        self.client.connect("localhost", 1883, 5)
        self.client.subscribe("light/#")
        self.client.loop_start()

    def initQt(self, numButtons, numLights):

        vbox = QVBoxLayout()
        
        for buttonIndex in range(numButtons):            
            button = QPushButton()
            vbox.addWidget(button)
            self.buttons.append(button)
            button.clicked.connect(partial(self.handle_button, str(buttonIndex), 'clicked'))

        for lightIndex in range(numLights):            
            light = QLabel()
            vbox.addWidget(light)
            self.lights.append(light)
        
        self.setLayout(vbox)
        self.setWindowTitle('IncludeMe')
        self.show()
        
    def handle_connect(self, client, userdata, flags, rc):
        print "Connected"

    def handle_message(self, client, userdata, msg):
        print( "Messaged" + msg.topic + " " + str(msg.payload))
        trimmedtopic = re.sub("^light/([0-9]+)$","\\1",msg.topic)
        if trimmedtopic != msg.topic:
            try:
                lightIndex = int(trimmedtopic)
                lightTarget = self.lights[lightIndex]
                lightTarget.setAutoFillBackground(True)
                lightTarget.setStyleSheet("background-color:" + msg.payload + ";")
            except:
                print "Issue passing color:" + msg.payload + " to label" , sys.exc_info()[0]

    def handle_button(self, buttonName, buttonState):
        self.client.publish("button/" + buttonName, buttonState)
        print "Pushed"

def main():
    app = QApplication(sys.argv)
    
    sender = Sender(2, 2)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()