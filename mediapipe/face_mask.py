import cv2
import mediapipe as mp

# Initialize Mediapipe Drawing and FaceMesh modules
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

# Open webcam
video = cv2.VideoCapture(0)

# Set up FaceMesh with detection & tracking confidence
with mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:
    while True:
        # Read a frame from the webcam
        ret, frame = video.read()
        if not ret:
            break  # Stop if no frame is captured

        # Convert frame to RGB for processing
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Process the image and detect face landmarks
        results = face_mesh.process(image)

        # Convert back to BGR for display
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw face mesh landmarks if detected
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    face_landmarks,
                    mp_face_mesh.FACEMESH_TESSELATION,
                    mp_drawing.DrawingSpec(thickness=1, circle_radius=1),  # Landmarks style
                    mp_drawing.DrawingSpec(thickness=1, circle_radius=1)   # Connection lines style
                )

        # Show the result in a window
        cv2.imshow('Face Mesh', image)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
video.release()
cv2.destroyAllWindows()
