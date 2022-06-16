import cv2
import time
import urllib.request
import numpy as np
import websockets
import asyncio
import json
import threading
from TimeUsing import TimeUsing
import HandTrackingModule as htm

from datetime import datetime   
################################
wCam, hCam = 640, 480
################################
import pyrebase

class startCamControl():

    def __init__(self, config, ws_ip, cam_ip,
                 led_room, cam_id, window_name, set_timer):
        self.config = config
        self.ws_ip = ws_ip
        self.cam_ip = cam_ip
        self.led_room = led_room
        self.cam_id = cam_id
        self.window_name = window_name
        
        timer = set_timer.split(",")
        self.night_time_on = timer[0]
        self.night_time_off = timer[1]
        currentTime = datetime.now().strftime("%H:%M")
        if(self.night_time_on <= currentTime and
           self.night_time_off >= currentTime):
                self.isNightTime = True
        else:
            self.isNightTime = False
        

        firebase = pyrebase.initialize_app(self.config)
        self.database = firebase.database()
        self.main()

    #Sending websocket funtion
    async def controlLED(self, cmd):
        async with websockets.connect('ws://' + self.ws_ip + '/ws') as websocket:
            sendData = {
                'id' : self.cam_id,
                'cmd' : cmd
            }
            sendDataJson = json.dumps(sendData)
            print("Sending..." + cmd)
            await websocket.send(sendDataJson)

    #Sync with firebase and call sending websocket function
    def runControl(self, cmd):
        if cmd == "TURN_ON":
            self.database.child(self.led_room).update({"mode" : "ON"})
            self.database.child(self.led_room).update({"time_on_off" : datetime.now().strftime("%H:%M:%S %d/%m/%Y")})
        elif cmd == "TURN_OFF":
            now = datetime.now()
            self.database.child(self.led_room).update({"mode" : "OFF"})
            time_on_off = self.database.child(self.led_room + "/time_on_off").get().val()
            date_format = "%H:%M:%S %d/%m/%Y"
            timeStart = datetime.strptime(time_on_off,date_format)
            timeEnd = now.strftime("%H:%M:%S %d/%m/%Y")
            seconds = int((datetime.strptime(timeEnd, date_format) - timeStart).total_seconds())
            timeUsing = {
                    "timeStart": time_on_off,
                    "timeEnd": timeEnd,
                    "seconds": seconds
                }
            self.database.child(self.led_room + "/details").push(timeUsing)
            self.database.child(self.led_room).update({"time_on_off" : datetime.now().strftime("%H:%M:%S %d/%m/%Y")})
            self.database.child(self.led_room).update({"time_on_off" : timeEnd})
        asyncio.run(self.controlLED(cmd))

    #Trigger when hand gesture is identified
    def startEvent(self, cmd):
        print("Preparing...")
        t1 = threading.Thread(target=self.runControl, args=(cmd,))
        t1.start()
        t1.join()
        time.sleep(2)

    def main(self):
        pTime = 0

        detector = htm.handDetector(mode=True, detectionCon=0.7)
        tipIds = [4,8,12,16,20]

        status = 0
        while True:
            currentTime = datetime.now().strftime("%H:%M")
            if(self.night_time_on <= currentTime and
               self.night_time_off >= currentTime and
               self.isNightTime == True):
                self.isNightTime = False;
                asyncio.run(self.controlLED("LED_BUILDIN_TURN_ON"))
            elif(self.night_time_off <= currentTime and self.isNightTime == False):
                self.isNightTime = True;
                asyncio.run(self.controlLED("LED_BUILDIN_TURN_OFF"))
            imgRes = urllib.request.urlopen('http://' + self.cam_ip + '/capture?')
            imgNp = np.array(bytearray(imgRes.read()), dtype=np.uint8)
            img = cv2.imdecode(imgNp, -1)
            img = cv2.resize(img, (640, 480))
            img = detector.findHands(img)
            lmList = detector.findPosition(img, draw=False)
            mode = self.database.child(self.led_room + "/mode").get().val()
                    
            #control by status from firebase
            #==================================
            if mode == "OFF":
                 if status == 0:
                     pass
                 else:
                     status = 0
                     self.startEvent("TURN_OFF")
            if mode == "ON":
                 if status == 1:
                     pass
                 else:
                     status = 1
                     self.startEvent("TURN_ON")
            #==================================
            
            #Control by hand gesture
            #============================================================
            if (len(lmList) != 0):
                fingers = []
                
                #Ngon cai
                if lmList[2][1] < lmList[17][1]:
                    #print("Tay trai")
                    if lmList[4][1] < lmList[3][1]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                else:
                    #print("Tay phai")
                    if lmList[4][1] > lmList[3][1]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                
                for id in range(1, 5):
                    if (lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]):
                        fingers.append(1)
                    else:
                        fingers.append(0)
                num_one = fingers.count(1)
                if num_one == 5 and mode == "OFF":
                    # turn on
                    status = 1
                    self.startEvent("TURN_ON")
                elif num_one == 0 and mode == "ON":
                    # turn off
                    status = 0
                    self.startEvent("TURN_OFF")

            cTime = time.time()
            fps = 1/(cTime - pTime)
            pTime = cTime
            
            cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN,
                        1, (255, 0, 0), 3)
            if self.window_name == "image1":
                cv2.imshow(self.window_name, img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cv2.destroyAllWindows()
