from Class_Sensor import Sensor
from Class_Camera import CCTV
from Class_Database import Database
from Class_Control import Control

def get_sensor(client = None, camera = None, control = None,database1 = None, database2 = None):
    return Sensor(client, camera, control,database1 ,database2)

def get_cctv(client, videoNumber = 0):
    return CCTV(client, videoNumber)

def get_database(client = None,host="localhost", port=8086, user="root",
                        password="root", database="None"):
    return Database(client, host, port, user, password, database)

def get_control(client, ledPin, coolingPin, waterPin1, waterPin2):
    return Control(client, ledPin, coolingPin, waterPin1, waterPin2)

def set_control(control):

    return {
                "led ON":control.on_LED,                "led OFF":control.off_LED,
                "cooling ON":control.on_Cooling,        "cooling OFF":control.off_Cooling,
                "water1 ON": control.on_LettuceWater,   "water1 OFF":control.off_LettuceWater,
                "water2 ON": control.on_ChoyWater,      "water2 OFF":control.off_ChoyWater
            }
