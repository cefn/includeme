#!/usr/bin/python
from __future__ import print_function

from threading import Thread

from twisted.internet.defer import Deferred
from twisted.trial.unittest import TestCase
from twisted.internet import reactor

from paho.mqtt.client import Client

class MqttTestCase(TestCase):

    def setUp(self):

        messaged = Deferred()
        receiver = Client()
        sender = Client()

        subscription = "button/1"

        def handle_receiver_messaged(client, userdata, msg):
            print("receiver_messaged...",end='')
            reactor.callFromThread(messaged.callback, msg)            

        def handle_sender_connected(client, userdata, flags, rc):
            print("sender_connected...",end='')
            receiver.on_message = handle_receiver_messaged
            sender.publish(subscription,"Hello World")
            
        def handle_receiver_subscribed(client, userdata, mid, granted_qos):
            print("receiver_subscribed...",end='')
            sender.on_connect = handle_sender_connected
            sender.connect("localhost", 1883, 5)
            sender.loop_start()

        def handle_receiver_connected(client, userdata, flags, rc):
            print("receiver_connected...",end='')
            receiver.on_subscribe = handle_receiver_subscribed
            receiver.subscribe(subscription)

        def connect_receiver():
            receiver.on_connect = handle_receiver_connected
            receiver.connect("localhost", 1883, 5)
            receiver.loop_start()

        self.sender = sender
        self.receiver = receiver
        self.messaged = messaged

        connect_receiver()

    def test_messaged(self):
        print("Running test_messaged successfully")
        return self.messaged
    
    # actually run within the receiver loop
    # (triggered by a message receive)
    def tearDown(self): 
        print("Running tearDown")
        self.sender.disconnect()
        self.receiver.disconnect()
        self.sender.loop_stop()  
        Thread(target=self.receiver.loop_stop).start() # join is otherwise called from the receiver's own thread
