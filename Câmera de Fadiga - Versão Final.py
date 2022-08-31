import cv2
import paho.mqtt.client as mqtt
import time

class fadiga(mqtt.Client):
    def on_connect(self, mqttc, obj, flags, rc):
        mqttc.subscribe("camerast")
        mqttc.subscribe("cansadost")
        
    def run(self):
        self.connect("broker.hivemq.com", 1883, 60)

client = fadiga("fadiga")
client.run()
        
Contador = 0
reiniciar = 0
a = ord('s')

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eyes_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml")

first_read = True

cap = cv2.VideoCapture(0)
ret, image = cap.read()

first_read == False
print("Reiniciar: ", reiniciar)
while ret:
    ret, image = cap.read()
    gray_scale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_scale = cv2.bilateralFilter(gray_scale, 5, 1, 1)
    faces = face_cascade.detectMultiScale(gray_scale, 1.3, 5, minSize=(200, 200))
    if len(faces) > 0:
        for (x, y, w, h) in faces:
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            eye_face = gray_scale[y:y + h, x:x + w]
            eye_face_clr = image[y:y + h, x:x + w]
            eyes = eyes_cascade.detectMultiScale(eye_face, 1.3, 5, minSize=(50, 50))
            if len(eyes) >= 2:
                if first_read:
                    cv2.putText(image, "Olhos detectados, pressione 's' para começar", (70, 70), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 255, 0), 2)
                else:
                    cv2.putText(image, "Olhos abertos", (70, 70), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255, 255, 255), 2)
                    reiniciar += 1
            else:
                if first_read:
                    cv2.putText(image, "Olhos nao encontrados", (70, 70), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255, 255, 255), 2)
                    reiniciar += 1
                else:
                    Contador += 1
                    cv2.putText(image, "Piscada detectada", (70, 70), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 255, 0), 2)
                    reiniciar += 1
                    cv2.imshow('image',image)
                    cv2.waitKey(1)
                    print("Piscada detectada", Contador)
                    print("Reiniciar: ", reiniciar)
                    if (Contador >= 308):
                        print("Motorista cansado")
                        client.publish("cansadost","Motorista cansado",0,True)
                    client.loop_start()
                    client.publish("camerast",Contador,0,True)
                    if (reiniciar >= 2670):
                        Contador = Contador * 0
                        reiniciar = reiniciar * 0
                        print("Reiniciando contagem")

    else:
        cv2.putText(image, "Face nao encontrada", (70, 70), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)
    cv2.imshow('image', image)
    reiniciar += 1
    a = cv2.waitKey(1)
    if 1 > 0:
        first_read = False
    if a == ord('q'):
        break

client.loop_stop()
cap.release()
cv2.destroyAllWindows()
