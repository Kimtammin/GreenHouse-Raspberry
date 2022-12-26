from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import json

class Database(object):
    
    # 데이터베이스 초기화
    def __init__(self, client, host="localhost",port=8086,
                user="root",password="root",database="None"):
        self.client = client
        
        self.database = InfluxDBClient(host,port,user,password,database)
        self.database.create_database(database)
        self.database.switch_database(database)

    # 데이터베이스 재설정
    def set_database(self,host,port,user,password,database):
        self.database = InfluxDBClient(host,port,user,password,database)
        self.database.create_database(database)
        self.database.switch_database(database)

    # 데이터베이스 저장
    def insert_database(self, table, temperature_out, humidity_out, temperature_in, humidity_in,
                        soil, time_id, state):
        
        json_body = [
            {
                "measurement" : table,
                "tags": {
                    "lettuce" : "lettuce",
                },
                "time" : time_id,
                "fields":{
                    "temperature_out": temperature_out,
                    "humidity_out"   : humidity_out,
                    "temperature_in" : temperature_in,
                    "humidity_in"    : humidity_in,
                    "soil"           : soil,
                    "state"          : state
                }
            }
        ]

        self.database.write_points(json_body)
        print("저장 완료")

    # select query
    def select_database(self,table):
        
        datas = self.database.query(f'select time, temperature_in, humidity_in,\
                                                    soil, state from "{table}"')
        if len(list(datas.get_points())) == 0:
            self.client.publish("database/data", "None")

        else: # 문자열 시간 -> 가공 -> 9시간 더해 KTC로 변경
            for data in datas.get_points():
                data_time_string = data['time'].replace('T',' ').replace('Z','')
                date = datetime.strptime(data_time_string, "%Y-%m-%d %H:%M:%S.%f") + timedelta(hours=9)
            
                data_list = [date.strftime("%Y-%m-%d %H:%M:%S"), str(data["temperature_in"]),
                            str(data["humidity_in"]), str(data["soil"]), data["state"]
                            ]
                data_string = " ".join(data_list)
                self.client.publish("database/data",data_string)