import cv2
import face_recognition
from collections import deque

reference_image_path = "profile.jpg"
reference_image = face_recognition.load_image_file(reference_image_path)
reference_face_encodings = face_recognition.face_encodings(reference_image)

if len(reference_face_encodings) > 0:
    reference_face_encoding = reference_face_encodings[0]
else:
    raise ValueError("No face found in the reference image.")

recognition_history = deque(maxlen=5)  

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # Assume unmatched initially
    label = "Unmatched"
    color = (0, 0, 255)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces([reference_face_encoding], face_encoding, tolerance=0.7)

        if True in matches:
            recognition_history.append("Matched")
        else:
            recognition_history.append("Unmatched")

        if recognition_history.count("Matched") > recognition_history.count("Unmatched"):
            label = "Matched"
            color = (0, 255, 0)
        else:
            label = "Unmatched"
            color = (0, 0, 255)

        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Display the frame
    cv2.imshow('Face Recognition', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
