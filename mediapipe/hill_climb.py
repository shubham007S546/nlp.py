import cv2
import mediapipe as mp
import numpy as np
import pydirectinput

# Initialize Mediapipe Holistic model
mp_holistic = mp.solutions.holistic

# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(3, 640)  # Width
cap.set(4, 480)  # Height

with mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=2,
    smooth_landmarks=True,
    enable_segmentation=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as holistic:

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            break

        # Flip the frame horizontally for a mirror effect
        img = cv2.flip(frame, 1)

        # Convert BGR to RGB for MediaPipe processing
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Process the image and detect holistic landmarks
        results = holistic.process(img_rgb)

        # Convert back to BGR for OpenCV visualization
        img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        height, width, _ = img.shape

        try:
            # Check if right hand landmarks are detected
            if results.right_hand_landmarks:
                right_hand = results.right_hand_landmarks.landmark
                right_hand_points = [(int(lm.x * width), int(lm.y * height)) for lm in right_hand]
                # Draw right hand landmarks in green
                cv2.polylines(img, [np.array(right_hand_points)], isClosed=False, color=(0, 255, 0), thickness=2)
            else:
                right_hand_points = []

            # Check if left hand landmarks are detected
            if results.left_hand_landmarks:
                left_hand = results.left_hand_landmarks.landmark
                left_hand_points = [(int(lm.x * width), int(lm.y * height)) for lm in left_hand]
                # Draw left hand landmarks in blue
                cv2.polylines(img, [np.array(left_hand_points)], isClosed=False, color=(255, 0, 0), thickness=2)
            else:
                left_hand_points = []

            # Define midpoint y-coordinate
            y_mid = height // 2
            pose = "move"

            # Control logic only if both hands detected with at least landmark index 1
            if len(right_hand_points) > 1 and len(left_hand_points) > 1:
                if (right_hand_points[1][1] < y_mid) and (left_hand_points[1][1] < y_mid):
                    pose = 'acc'
                    pydirectinput.keyDown('up')
                    pydirectinput.keyUp('down')
                elif (right_hand_points[1][1] < y_mid) and (left_hand_points[1][1] > y_mid):
                    pose = 'brake'
                    pydirectinput.keyDown('down')
                    pydirectinput.keyUp('up')
                else:
                    # Release keys if no gesture
                    pydirectinput.keyUp('up')
                    pydirectinput.keyUp('down')
            else:
                # No hands detected or incomplete, release keys
                pydirectinput.keyUp('up')
                pydirectinput.keyUp('down')

            # Draw current pose text on the frame
            cv2.putText(img, pose, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 255), 2, cv2.LINE_AA)
            # Draw midline for reference
            cv2.line(img, (0, y_mid), (width, y_mid), (255, 255, 255), 2)

        except Exception as e:
            # If error occurs (e.g. no hands detected), print error and continue
            print(f"Error in landmark processing: {e}")

        # Display the frame
        cv2.imshow('cargame', img)

        # Press 'q' key to exit
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()
