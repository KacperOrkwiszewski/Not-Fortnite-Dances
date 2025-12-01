from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Mapa nazw
LANDMARK_NAMES = {
    0: "Nos", 11: "L. ramie", 12: "P. ramie",
    15: "L. nadgarstek", 16: "P. nadgarstek",
    23: "L. biodro", 24: "P. biodro",
    25: "L. kolano", 26: "P. kolano",
    27: "L. kostka", 28: "P. kostka"
}

def draw_landmarks_on_image(rgb_image, detection_result):
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = np.copy(rgb_image)

    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            solutions.pose.POSE_CONNECTIONS,
            solutions.drawing_styles.get_default_pose_landmarks_style())
    return annotated_image

def draw_values_on_image(rgb_image, detection_result):
    """
    Rysuje wartości RZECZYWISTE (w metrach) w miejscu punktów na ekranie.
    """
    pose_landmarks_list = detection_result.pose_landmarks
    pose_world_landmarks_list = detection_result.pose_world_landmarks
    
    annotated_image = np.copy(rgb_image)
    height, width, _ = annotated_image.shape

    # Sprawdzenie czy mamy oba zestawy danych
    if not pose_landmarks_list or not pose_world_landmarks_list:
        return annotated_image

    # Punkty do wyświetlenia (żeby nie zakryć całego obrazu)
    TARGET_LANDMARKS = [0, 15, 16, 11, 12] # Nos, nadgarstki, ramiona
    #TARGET_LANDMARKS = range(33)

    # Iterujemy po wykrytych osobach
    for idx in range(len(pose_landmarks_list)):
        screen_landmarks = pose_landmarks_list[idx]       # Do pozycji na ekranie
        world_landmarks = pose_world_landmarks_list[idx]  # Do wartości liczbowych
        
        for lm_id in TARGET_LANDMARKS:
            # Pobieramy odpowiedni punkt z obu list
            lm_screen = screen_landmarks[lm_id]
            lm_world = world_landmarks[lm_id]

            # Obliczamy pozycję napisu na ekranie (używając landmarków ekranowych!)
            cx, cy = int(lm_screen.x * width), int(lm_screen.y * height)

            name = LANDMARK_NAMES.get(lm_id, f"ID:{lm_id}")
            
            # Tworzymy napis z wartościami RZECZYWISTYMI (World)
            # Wartości są w metrach.
            coord_text = f"{name} ({lm_world.x:.2f}m, {lm_world.y:.2f}m, {lm_world.z:.2f}m)"

            # Rysowanie tekstu (czarny obrys + biały środek)
            cv2.putText(annotated_image, coord_text, (cx + 10, cy), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(annotated_image, coord_text, (cx + 10, cy), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 255, 100), 1, cv2.LINE_AA) # Lekko zielony kolor

    return annotated_image

if __name__ == "__main__":
    base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True)
    detector = vision.PoseLandmarker.create_from_options(options)

    cap = cv2.VideoCapture("v_test.mp4")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Błąd kamery")
            break

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        
        # Detekcja
        detection_result = detector.detect(mp_image)

        # Rysowanie szkieletu (standardowe)
        annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), detection_result)
        
        # Rysowanie wartości rzeczywistych 3D
        annotated_image = draw_values_on_image(annotated_image, detection_result)

        cv2.imshow("Wspolrzedne Rzeczywiste (Metry)", cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()