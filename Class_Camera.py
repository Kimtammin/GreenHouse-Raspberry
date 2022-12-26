import cv2 as cv

class CCTV(object):

    # 카메라 초기화
    def __init__(self, client, videoNumber = 0):
        self.client = client
        self.cap = cv.VideoCapture(videoNumber, cv.CAP_V4L)
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.size_value = 0
        self.width = 20
        self.height = 10

        self.iscam = False
    # CCTV ON
    def on_Camera(self, path = "/home/pi/min/SmartFarmProject/image_write_b"):
        
        while self.iscam:
            try:
                ret, img_frame = self.cap.read()
                if ret is False:
                    print("Not Image Capture")
                    break
                
                size_width  = self.width * self.size_value
                size_height = self.height * self.size_value
                frame = img_frame[0 + size_height : 479 - size_height, 0 + size_width : 639-size_width].copy()
                img_frame_resize = cv.resize(frame, (640,480),interpolation=cv.INTER_AREA)

                cv.imwrite(path+"/frame.jpg", img_frame_resize)

                file = open(path+"/frame.jpg",'rb')
                filecontent = file.read()
                byteArr = bytearray(filecontent)

                self.client.publish('streaming/cam1', byteArr)

            except Exception as e:
                print(e)

    
    # Image Captrue
    def capture_Camera(self, now, path = "/home/pi/min/SmartFarmProject/image_time/"):
        ret, image = self.cap.read()

        if ret is False:
            print("Not Image Captrue")
        else:
            cv.imwrite(path+f"{now}.jpg", image)

