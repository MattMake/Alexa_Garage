""" 
   Author: Originally Surendra Kane
   Edited by: shrocky2
   Script to control your Garge Door using an Amazon Echo. 
"""

import fauxmo
import logging
import time


#GPIO Added Information
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Name the GPIO PINs
garagecontrol_1 = 15
garagelights_1 = 16
garagesensor_1 = 7

# Match pinList to your Relay PINs
pinList = [garagecontrol_1, garagelights_1]
for i in pinList:
        GPIO.setup(i, GPIO.OUT)
        GPIO.output(i, GPIO.HIGH)
switchList = [garagesensor_1]
for i in switchList:
        GPIO.setup(i, GPIO.IN, GPIO.PUD_UP)  # PUD_UP - open = true, closed = false

time.sleep(.5)
#End GPIO Added Information


from debounce_handler import debounce_handler
logging.basicConfig(level=logging.DEBUG)

print (" Control+C to exit program")
#Edit this section to personalize your TV Channels. The channel number is listed after each station.
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
channels = {'Garage Door':10001,
            'Garage Lights':10002}  # added end bracket, remove if you add more items
#            'Item 2':10003,    # commented out extra line items 
#            'Item 3':10004,    # to keep Alexa from finding unnecessary items
#            'Item 4':10005}
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------


class device_handler(debounce_handler):
    """Triggers on/off based on 'device' selected.
       Publishes the IP address of the Echo making the request.
    """
    TRIGGERS = {"Garage Door":50001,
                "Garage Lights":50002}   # added end bracket, remote if you add more items
#               "Item 2":50003,         # commented to remove extra items
#               "Item 3":50004,
#               "Item 4":50005}

    def trigger(self,port,state):
      if state == True: #If the ON command is given, it will run this code
           if port == 10001: #Open/Close Garage Door
                # check if garage is open already
                if GPIO.input(garagesensor_1):
                     print('Garage is Open Already')
                else:
                     GPIO.output(garagecontrol_1, GPIO.LOW)
                     time.sleep(.5)  #adjusted time to 1/2 second
                     GPIO.output(garagecontrol_1, GPIO.HIGH)
                     print ("Open Garage Door")
           print " "
           if port == 10002: #Turn on garage lights (2nd relay port)
                GPIO.output(garagelights_1, GPIO.LOW)
                print ('Turning on Garage Lights')
      else: #If the OFF command is given, it will run this code
           if port == 10001: #Open/Close Garage Door
                # check if garage is closed already
                if GPIO.input(garagesensor_1):
                     GPIO.output(garagecontrol_1, GPIO.LOW)
                     time.sleep(.5)  #adjusted time to 1/2 second
                     GPIO.output(garagecontrol_1, GPIO.HIGH)
                     print ("Close Garage Door")
                else:
                     print ("Garage is already closed")
           if port == 10002: # Turn off garage lights (2nd relay port)
                GPIO.output(garagelights_1,GPIO.HIGH)
                print ('Turning off Garage Lights')
      print " "

    def act(self, client_address, state, name):
        print ("State", state, "on", name, "from client @", client_address, "port:",channels[str(name)])
        self.trigger(channels[str(name)],state)
        return True

if __name__ == "__main__":
    # Startup the fauxmo server
    fauxmo.DEBUG = True
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    # Register the device callback as a fauxmo handler
    d = device_handler()
    for trig, port in d.TRIGGERS.items():
        fauxmo.fauxmo(trig, u, p, None, port, d)

    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    print " "
    while True:
        try:
            # Allow time for a ctrl-c to stop the process
            p.poll(100)
            time.sleep(0.1)
        except Exception, e:
            logging.critical("Critical exception: " + str(e))
            break
