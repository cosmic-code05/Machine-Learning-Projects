import cv2
import mediapipe as mp
import math
import numpy as np
import screen_brightness_control as sbc

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('Video.mp4', fourcc, 20.0, (250,250))

hands = mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]

            distance = math.hypot(thumb_tip.x - index_tip.x, thumb_tip.y - index_tip.y)

            vol_percent = np.interp(distance, [0.03, 0.15], [0, 100])
            vol_scalar = vol_percent / 100
            volume.SetMasterVolumeLevelScalar(vol_scalar, None)

            bar_fill = np.interp(vol_percent, [0, 100], [350, 150])

            cv2.rectangle(frame, (50, 150), (75, 350), (255, 255, 255), 1)
            cv2.rectangle(frame, (50, int(bar_fill)), (75, 350), (255, 255, 255), cv2.FILLED)
            cv2.putText(frame, f'{int(vol_percent)}%', (40, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)

            bright_value = np.interp(distance, [0.04, 0.20], [0, 100])
            sbc.set_brightness(int(bright_value))

    out.write(frame)
    cv2.imshow("Window", frame)

    if cv2.waitKey(1) & 0xFF == ord('x'):
        break

out.release()
cap.release()
cv2.destroyAllWindows()