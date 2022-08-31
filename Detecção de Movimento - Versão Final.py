import cv2, time, pandas
from datetime import datetime
import paho.mqtt.client as mqtt

class deteccao(mqtt.Client):
    def on_connect(self, mqttc, obj, flags, rc):
        mqttc.subscribe("movimentost")

    def run(self):
        self.connect("broker.hivemq.com", 1883, 60)

client = deteccao("deteccao")
client.run()
        
static_back = None
  
motion_list = [ None, None ]
  
time = []

video = cv2.VideoCapture(0)
  
while True:
    check, frame = video.read()
  
    motion = 0
  
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
  
    if static_back is None:
        static_back = gray
        continue
  
    diff_frame = cv2.absdiff(static_back, gray)
  
    thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)
  
    cnts,_ = cv2.findContours(thresh_frame.copy(), 
                       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
  
    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
        motion = 1
        print("Movimento detectado")
        client.loop_start()
        client.publish("movimentost","Movimento detectado",0,True)
  
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

    motion_list.append(motion)
  
    motion_list = motion_list[-2:]

    if motion_list[-1] == 1 and motion_list[-2] == 0:
        time.append(datetime.now())
  
    if motion_list[-1] == 0 and motion_list[-2] == 1:
        time.append(datetime.now())
  
    cv2.imshow("Gray Frame", gray)

    cv2.imshow("Difference Frame", diff_frame)
  
    cv2.imshow("Threshold Frame", thresh_frame)
  
    cv2.imshow("Color Frame", frame)
  
    key = cv2.waitKey(1)
    if key == ord('q'):
        if motion == 1:
            time.append(datetime.now())
        break
    
client.loop_stop()
video.release()
cv2.destroyAllWindows()
