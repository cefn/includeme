import sys
import time
import getopt
import alsaaudio

def usage():
    sys.stderr.write('usage: recordtest.py [-c ] \n')
    print 'haha4'
    sys.exit(2)

if __name__ == '__main__':
    
    print 'haha1'
    
    card = 'default'

    opts, args = getopt.getopt(sys.argv[1:], 'c:')
    for o, a in opts:
        if o == '-c':
            card = a

        if not args:
            usage()
    f = open(args[0], 'wb')
    # Open the device in nonblocking capture mode. The last argument could
    # just as well have been zero for blocking mode. Then we could have
    # left out the sleep call in the bottom of the loop
    
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, card)
    
    # Set attributes: Mono, 44100 Hz, 16 bit little endian samples
    
    inp.setchannels(1)
    inp.setrate(44100)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    
    # The period size controls the internal number of frames per period.
    # The significance of this parameter is documented in the ALSA api.
    # For our purposes, it is suficcient to know that reads from the device
    # will return this many frames. Each frame being 2 bytes long.
    # This means that the reads below will return either 320 bytes of data
    # or 0 bytes of data. The latter is possible because we are in nonblocking
    # mode.
    
    inp.setperiodsize(48)

    print 'haha2'
    loops = 100
    while loops > 0:
        print 'haha3'
        loops -= 1
        # Read data from device
        l, data = inp.read()
        print len(data)
        print l
        if l:
            f.write(data)
            time.sleep(.001)
