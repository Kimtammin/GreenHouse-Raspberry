import paho.mqtt.client as mqtt
from threading import Thread
import Class_Set_Retrun as obj
import board

# Broker 연결 성공하면 Page별 통신 대기
def on_connect(client, userdata, flags, rc):
    print("MQTT Broker 연결 성공")
    client.subscribe("page/#")

# page/# 토픽으로 통신이 올 때마다
def on_message(client, userdata, message):
    global cctv_thread

    msg     = message.payload.decode("utf-8")
    topic   = message.topic.split('/')
    print(f"토픽 : {message.topic}, 메세지 : {msg}")

    # Main Page이면 현재 센서값 전송 및 실시간전송 ON
    if topic[1] == "main":
        sensor.publish()
        sensor.ispub = True
    
    # CCTV Page이면 센서값 전송 종료 및 버튼감지
    elif topic[1] == "cctv":
        sensor.ispub = False
        if msg == "cctv_on":
            cctv.iscam   = True
            cctv_thread  = Thread(target = cctv.on_Camera)
            cctv_thread.start()
            print("카메라 ON")
        
        elif msg == "cctv_off":
            cctv.iscam = False
            cctv_thread.join()
            print("카메라 OFF")

        elif msg[0].isdigit():
            cctv.size_value = int(msg[0])

    # Data Page이면 센서값 전송 종료 및 쿼리
    elif topic[1] == "data":
        sensor.ispub = False
        if topic[1] != msg:
            value, table = msg.split(' ')
            if value == "lettuce":
                lettuce_db.select_database(table)
            else:
                choy_db.select_database(table)

    # Control Page이면 제어 대기
    elif topic[1] == "control":
        if topic[1] != msg:
            controlBOX[msg]()

if __name__ == "__main__":
    # MQTT Broker 연결"/home/pi/min/SmartFarmProject/image_time"
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("192.168.1.36") 

    # 기능 인스턴스 생성
    cctv        = obj.get_cctv(client, 0)
    control     = obj.get_control(client, 12, 16, 26, 19)
    lettuce_db  = obj.get_database(client,host="localhost",port=8086, user="pi", password="1234", database="lettuce_database")
    choy_db     = obj.get_database(client,host="localhost",port=8086, user="pi", password="1234", database="choy_database")
    sensor      = obj.get_sensor(client, cctv, control, lettuce_db,choy_db)
    sensor.set_pin(board.D4, board.D17, 20)
    sensor.set_lcd(0x27)

    # 제어 인스턴스 생성
    controlBOX  = obj.set_control(control)

    # 쓰레드 생성
    sensor_thread = Thread(target=sensor.on_Greenhouse, args=(True,0,1))
    lcd_thread    = Thread(target=sensor.on_Display)
    cctv_thread   = None

    # 쓰레드 동작 및 통신 대기
    sensor_thread.start()
    lcd_thread.start()
    try:
        client.loop_forever()
    except  KeyboardInterrupt:
        exit(1)