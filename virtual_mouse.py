import cv2
import mediapipe as mp
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

class GestureController:
    def __init__(self):
        self.gc_mode = 1
        self.cap = cv2.VideoCapture(0)
        self.CAM_HEIGHT = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.CAM_WIDTH = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.dom_hand = True
        self.prev_index_finger_x = None

    def classify_hands(self, results):
     left, right = None, None
     for hand_landmarks in results.multi_hand_landmarks:
        handedness = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x

        if handedness < 0.5:
            left = hand_landmarks
        else:
            right = hand_landmarks

     if self.dom_hand:
        self.hr_major = right
        self.hr_minor = left
     else:
        self.hr_major = left
        self.hr_minor = right

    def swing_action(self, index_finger_tip_x):
        if self.prev_index_finger_x is not None:
            delta_x = index_finger_tip_x - self.prev_index_finger_x

            if delta_x > 0.1:  # Swing from left to right
                pyautogui.hotkey('alt', 'tab', 'right')
            elif delta_x < -0.1:  # Swing from right to left
                pyautogui.hotkey('alt', 'tab', 'left')

        self.prev_index_finger_x = index_finger_tip_x

    def move_mouse(self, hand_landmarks):
        if hand_landmarks:
            screen_width, screen_height = pyautogui.size()
            index_finger_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
            index_finger_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            new_x = int(index_finger_tip_x * screen_width)
            new_y = int(index_finger_tip_y * screen_height)
            pyautogui.moveTo(new_x, new_y)

    def start(self):
        with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            while self.cap.isOpened() and self.gc_mode:
                success, image = self.cap.read()

                if not success:
                    print("Ignoring empty camera frame.")
                    continue

                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    self.classify_hands(results)

                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        self.move_mouse(hand_landmarks)

                cv2.imshow('Hand Tracking', image)
                if cv2.waitKey(5) & 0xFF == 13:
                    break

        self.cap.release()
        cv2.destroyAllWindows()

gc1 = GestureController()
gc1.start()
