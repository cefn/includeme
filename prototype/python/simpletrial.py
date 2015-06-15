from threading import Thread
from time import sleep

from twisted.trial.unittest import TestCase
from twisted.internet.defer import Deferred
from twisted.internet import reactor

class ThreadTestCase(TestCase):

    def setUp(self):
        pass
    
    def test_delay(self):
        messaged = Deferred()
        def delaycallback():
            sleep(2)
            reactor.callFromThread(messaged.callback, True)
        Thread(target=delaycallback).start()
        return messaged
    
    def tearDown(self):
        pass