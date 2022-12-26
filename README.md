# GreenHouse-Raspberry
SmartFarm Project - GreenHouse Raspberry PI

# 소개
Raspberry PI를 사용하여 외부 온습도 및 내부 온습도, 토양수분, 물의 양과 상태를 확인한다.</br>
Python을 사용하여 통신, 데이터베이스 저장, 카메라, 센싱 컨트롤 등 GreenHouse, 온실의 심장역할</br>

</br>
</br>
### 사용 API

* openCV
* Thread
* MQTT
* GPIO
* InfluxDBClient
* json
* adafruit_dht
* spidev
* RPi_I2C_driver

### flowChart
![Raspberry_flow_chart_last](https://user-images.githubusercontent.com/98437996/209539156-8ae10f60-0c4a-4ebb-b152-234e1697ebc6.png)


# 설명
기본적으로 2개의 서브 쓰레드와 메인 루프가 존재합니다.</br>
main loop의 경우 mqtt 통신을 위해 지속적으로 메세지가 전달됬는지 확인하기 위한 루프이며</br>
sensor thread는 정해진 시간마다 온습도, 토양수분, 현재 시간 등을 읽어 데이터베이스 저장하고 web에게 publish할지 선택합니다.</br>
lcd thread는 5초마다 외부 온습도 및 상추 토양수분 , 내부 온습도 및 청경채 토양수분을 프린트하여 출력합니다. </br>
cctv thread는 web에서 button을 누른 경우만 쓰레드가 동작합니다.</br>
모든 객체는 Class_Set_Return 파일을 import하여 생성할 수 있습니다.</br>

# Sensor Class
Sensor(client, camera, control, database1, database2)</br>
* 기본적으로 클라이언트, 카메라 객체, 컨트롤 객체, 데이터베이스 객체를 받습니다. 지정해 주지않으면 None입니다.
* set_pin(dht핀 번호, dht 핀 번호, 수위센서 핀번호) 메서드로 핀을 초기화합니다.
* set_lcd(주소) 메서드로 lcd를 초기화 할 수 있습니다.
* on_Greenhouse(isData = False, 토양수분채널, 토양수분채널) 메서드로 센싱을 시작합니다. isData = False는 데이터베이스 저장을 안하겠다는 의미
* on_Display() 메서드로 lcd를 실행시킵니다.
* publish() 메서드는 json text형태로 메세지를 전달합니다.
</br>
</br>
</br>

# Data Class
Database(client, host, port,user, password, database)</br>
* 기본적으로 클라이언트 및 데이터베이스 생성을 위해 호스트, 포트, 유저ID, 유저 Password, database이름을 지정합니다.(Influxdb가 설치되어 있는 경우)
* set_database(host, port, user, password, database)로 데이터베이스 재설정이 가능합니다.
* insert_database(테이블명, 외부온도, 외부습도, 내부온도, 내부습도, 토양수분, 시간, 상태) 메서드로 연결된 데이터베이스에 데이터를 저장합니다.
* influxdb의 특성상 테이블이 존재하면 시간순으로 데이터를 쌓아주고 테이블이 없다면 CREATE명령없이 바로 만든 후 데이터를 저장합니다.
* web에서 과거 데이터를 받거나 현재 저장된 데이터를 받고 싶을 때 select_database가 호출됩니다.
* select_dataabase(table) 메서드는 연결된 데이터베이스에서 query를 통해 데이터를 찾아주고 데이터가 없으면 None 메세지를 데이터가 있다면 모든 데이터를 text형식으로 전달합니다.
</br>
</br>
</br>
# Camera Class
Camera(client, 비디오 번호)</br>
* 클라이언트와 raspberry PI에 연결된 카메라 번호를 넣어 초기화합니다.
* web에서 카메라 on 버튼을 누르면 서브 쓰레드가 동작하여 이미지를 읽고 저장하고 binary로 읽은 후 전달합니다.
* capture_Camera(now, path) 메서드를 사용하여 이미지를 캡쳐한후 정해진 경로에 저장합니다.
* 제 프로젝트는 한시간 단위로 온실 속 환경을 찍어 저장합니다.
</br>
</br>
</br>
# Control Class
Control(client, ledpin, coolingpin, waterPin1,waterPin2)</br>
* 라즈베리파이와 연결된 핀번호를 초기화합니다.
* 기본으로는 web에서 제어하며 밤 시간의 경우에는 스스로 판단하여 작동하도록 되어있습니다.
</br>
</br>
</br>
# Main
1. mqtt broker 연결
2. sensor, database, control, cctv 인스턴스 생성 및 초기화
3. thread 객체 생성
4. sensor thread, lcd thread 시작 및 mqtt loopforever
5. 메세지가 온다면 지속적으로 함수 실행으로 그에 맞는 행동을 취한다.
</br>
</br>
</br>
# 시각화
라즈베리파이의 influxdb를 사용하여 grafana와 연동해 실시간 데이터를 시각화 할 수 있습니다.</br>
데이터베이스를 설정하여 자신에게 맞는 테이블을 설정하여 패널을 만들어 주세요.</br>
![grafana_img2 PNG](https://user-images.githubusercontent.com/98437996/209542232-0ca2ce14-cb35-46dd-b3a7-75c6604ffec7.png)
![grafana_img3 PNG](https://user-images.githubusercontent.com/98437996/209542236-ce870910-8e65-4975-b579-a6581a6fbb33.png)
</br>
</br>
</br>
# 마무리
Raspberry의 경우 사용되는 보드나, 센서에 따라 작동하지 않을 수 있으며 기본적으로 mosquitto broker가 열려있을 때 실행이
가능합니다.</br>
각 클래스는 디폴트 값이 존재하며 데이터베이스나 install 되어있지 않은 API가 존재하면 사용하지 않아도 됩니다.</br>

* 프로젝트 담당자 : 김태민
* 개발 인원 : 3명
* 문의 : kkc8833@gmail.com
* 
