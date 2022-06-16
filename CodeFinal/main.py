from TurnOnOff import startCamControl
import threading

config = {
    "apiKey": "AIzaSyD-gAhds1PvCOyEv79CLKX2bNHQ3UkBKrg",
    "authDomain": "fir-led-f0542.firebaseapp.com",
    "projectId": "fir-led-f0542",
    "databaseURL": "https://fir-led-f0542-default-rtdb.firebaseio.com/",
    "storageBucket": "fir-led-f0542.appspot.com",
    "messagingSenderId": "449283292826",
    "appId": "1:449283292826:android:fe89bbd8e363487816a923",
}

ws_ip = "192.168.0.110:8888"

window_name1 = "image1"
cam1_ip = "192.168.0.107"
led_room1 = "leds/led_livingroom"
set_timer_night_time = "17:30,22:30"

window_name2 = "image2"
cam2_ip = "192.168.61.108"
led_room2 = "leds/led_bedroom"

cam_1 = threading.Thread(
    target=startCamControl,
            args=(config, ws_ip, cam1_ip,
                  led_room1, '1', window_name1,
                  set_timer_night_time))
#cam_2 = threading.Thread(
#    target=startCamControl,
#            args=(config, ws_ip, cam2_ip,
#                  led_room2, '2', window_name2,
#                  set_timer_night_time))

cam_1.start()
#cam_2.start()

cam_1.join()
#cam_2.join()
