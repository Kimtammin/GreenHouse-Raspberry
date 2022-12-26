import RPi.GPIO as GPIO
import time

class Control(object):

    # 핀 초기화
    def __init__(self, client, led, cooling, waterPin1, waterPin2):
        self.client           = client
        self.ledPin           = led
        self.coolingPin       = cooling
        self.lettuce_waterPin = waterPin1
        self.choy_waterPin    = waterPin2

        self.isLED     = False
        self.isWater   = False
        self.isCooling = False
        self.set_GPIO()
    
    # GPIO 초기화
    def set_GPIO(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ledPin, GPIO.OUT)
        GPIO.setup(self.coolingPin, GPIO.OUT)
        GPIO.setup(self.lettuce_waterPin, GPIO.OUT)
        GPIO.setup(self.choy_waterPin, GPIO.OUT)

    # LED
    def on_LED(self):
        print("LED ON")
        GPIO.output(self.ledPin, GPIO.LOW)
        self.isLED = True

    def off_LED(self):
        print("LED OFF")
        GPIO.output(self.ledPin, GPIO.HIGH)
        self.isLED = False
    
    # Cooling Fan
    def on_Cooling(self):
        print("Cooling Fan ON")
        GPIO.output(self.coolingPin, GPIO.LOW)
        self.isCooling = True
    
    def off_Cooling(self):
        print("Cooling Fan OFF")
        GPIO.output(self.coolingPin, GPIO.HIGH)

    # Water Pump
    def on_LettuceWater(self):
        print("Lettuce Water ON")
        self.isWater = True
        GPIO.output(self.lettuce_waterPin, GPIO.LOW)
        time.sleep(10)
        self.off_LettuceWater()
    
    def off_LettuceWater(self):
        print("Lettuce Water OFF")
        self.isWater = False
        GPIO.output(self.lettuce_waterPin, GPIO.HIGH)
        self.client.publish("control/pump","let_water")

    def on_ChoyWater(self):
        print("Choy Water ON")
        self.isWater = True
        GPIO.output(self.choy_waterPin, GPIO.LOW)
        time.sleep(10)
        self.off_ChoyWater()

    def off_ChoyWater(self):
        print("Choy Water OFF")
        self.isWater = False
        GPIO.output(self.choy_waterPin, GPIO.HIGH)
        self.client.publish("control/pump", "choy_water")