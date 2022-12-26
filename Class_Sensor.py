import RPi.GPIO as GPIO
import adafruit_dht
import spidev
import RPi_I2C_driver

import time
from datetime import datetime, timedelta
import json
# set client, database, control 할수있게 메서드 추가
class Sensor(object):

    # 브로커, 데이터베이스, 컨트롤 초기화
    def __init__(self, client, camera, control, database1, database2):
        self.client           = client
        self.camera           = camera
        self.control          = control
        self.lettuce_database = database1
        self.choy_database    = database2

        self.temperature_inner = 0
        self.humidity_inner    = 0
        self.temperature_outer = 0
        self.humidity_outer    = 0
        self.soil_lettuce      = 0
        self.soil_choy         = 0
        self.hour              = 0

        self.ispub = False
        self.isbreak = False
    
    # 라즈베리파이 핀 초기화
    def set_pin(self,dht_inner, dht_outer, water):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(water, GPIO.IN)
        self.water     = water
        self.dht_inner = adafruit_dht.DHT22(dht_inner)
        self.dht_outer = adafruit_dht.DHT11(dht_outer)
        self.spi       = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz = 1000000

    # LCD 초기화
    def set_lcd(self, address):
        self.lcd = RPi_I2C_driver.lcd(address)

        temperatrue_icon = [
            0b00100,
            0b01010,
            0b01010,
            0b01110,
            0b01110,
            0b11111,
            0b11111,
            0b01110
        ]

        humidity_icon    = [
            0b00100,
            0b00100,
            0b01010,
            0b01010,
            0b10001,
            0b10001,
            0b10001,
            0b01110
        ]

        self.lcd.createChar(0,temperatrue_icon)
        self.lcd.createChar(1,humidity_icon)

    # spi 계산 (단위 : %)
    def readadc(self, adcnum):
        if adcnum > 7 or adcnum < 0:
            return -1
        read = self.spi.xfer2([1,(8+adcnum) << 4, 0])
        data = ((read[1] & 3) << 8) + read[2]
        
        return round(100.0 - ((data * 100) / float(642)), 1)

    # 센서 동작(데이터베이스 자동저장)
    def on_Greenhouse(self,isData = False,lettuce_num = 0, choy_num = 1):
        while True:
            try:
                if self.isbreak:
                    break
                # 센싱
                self.temperature_inner = self.dht_inner.temperature
                self.humidity_inner    = self.dht_inner.humidity
                self.temperature_outer = self.dht_outer.temperature
                self.humidity_outer    = self.dht_outer.humidity
                self.soil_lettuce      = self.readadc(lettuce_num)
                self.soil_choy         = self.readadc(choy_num)
                self.water_level       = "Suffice" if GPIO.input(self.water) == 1 else "lack"
                
                if self.temperature_inner == None or self.humidity_inner == None \
                        or self.temperature_outer == None or self.humidity_outer == None:
                    raise Exception()
                
                state = "Red" if self.temperature_inner < 15 and self.humidity_inner < 30 else "Green"

                current_time = datetime.now()
                # InfluxDB는 UTC기반 KCT->UTC 로 변경
                utc_time     = current_time - timedelta(hours=9)
                measurement  = current_time.strftime("%Y-%m-%d")
                
                if self.hour != current_time.hour:
                    self.camera.capture_Camera(current_time.strftime("%Y-%m-%d %H:%M"))
                    self.hour = current_time.hour

                # 저장
                if isData and self.lettuce_database != None and self.choy_database != None:
                    self.lettuce_database.insert_database(measurement, self.temperature_outer, self.humidity_outer, self.temperature_inner, self.humidity_inner, 
                                                            self.soil_lettuce, utc_time, state)
                    self.choy_database.insert_database(measurement,self.temperature_outer, self.humidity_outer, self.temperature_inner, self.humidity_inner, 
                                                            self.soil_choy, utc_time, state)
                
                
                # 데이터 전달
                if self.ispub:
                   self.publish()

                # 현재시간이 밤이면 자동 18시 ~ 09시
                if 18 <= current_time.hour <= 23 or 0 <= current_time.hour <=8:
                    self.autoMode()

            except Exception as e:
                print(e)
                time.sleep(1)
            else:
                time.sleep(30)

    # lcd 동작 
    def on_Display(self):
        while True:
            if self.isbreak:
                break
            
            self.lcd.clear()
            self.lcd.noCursor()
            self.lcd.setCursor(1, 0)
            self.lcd.write(0)
            self.lcd.print(f": {self.temperature_inner}")
            self.lcd.setCursor(9, 0)
            self.lcd.write(1)
            self.lcd.print(f": {self.humidity_inner}")
            self.lcd.setCursor(2, 1)
            self.lcd.print(f"lettuce : {self.soil_lettuce}")
            time.sleep(5)
            self.lcd.clear()
            self.lcd.noCursor()
            self.lcd.setCursor(1, 0)
            self.lcd.write(0)
            self.lcd.print(f": {self.temperature_outer}")
            self.lcd.setCursor(9, 0)
            self.lcd.write(1)
            self.lcd.print(f": {self.humidity_outer}")
            self.lcd.setCursor(3, 1)
            self.lcd.print(f"choy : {self.soil_choy}")
            time.sleep(5)
    
    # 스스로 판단
    def autoMode():
        # LED는 항상 킨다.
        if not self.control.isLED:
            self.control.led_ON()

        # 온도가 적정 온도 이상이거나 습도가 너무 높으면
        if self.temperature_inner > 20 or self.humidity_inner > 50:
            if not self.control.isCooling:
                self.control.cooling_ON()

        else:
            if self.control.isCooling:
                self.control.cooling_OFF()

        # 토양수분이 부족하면 (수정)
        if soil_lettuce < 15:
            if not self.control.isWater:
                self.control.let_waterON()
        
        if soil_choy < 15:
            if not self.control.isWater:
                self.control.choy_waterON()


    
    # 데이터 전송
    def publish(self):
        datas = {"temperature_inner" : self.temperature_inner, "humidity_inner":self.humidity_inner,
                            "temperature_outer":self.temperature_outer, "humidity_outer":self.humidity_outer,
                            "soil_lettuce": self.soil_lettuce, "soil_choy":self.soil_choy, "water_level":self.water_level}
        print(datas)
        json_datas = json.dumps(datas)
        self.client.publish("sensor/data",json_datas)