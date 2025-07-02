import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
from sklearn.preprocessing import OneHotEncoder

# Load YOLOv11 model
model = YOLO("./yolo/best.pt")
EXCEL_FILE_PATH = "./food-features.xlsx"

# ArUco marker dictionary and detector
ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
parameters = cv2.aruco.DetectorParameters()
aruco_detector = cv2.aruco.ArucoDetector(ARUCO_DICT, parameters)
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
df_food_features = pd.read_excel(EXCEL_FILE_PATH)
encoder.fit(df_food_features[['Food_type']])

def detect_aruco_marker(image, marker_length_cm=5):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = aruco_detector.detectMarkers(gray)
    if ids is not None:
        marker_pixel_width = np.linalg.norm(corners[0][0][0] - corners[0][0][1])
        pixel_per_cm = marker_pixel_width / marker_length_cm
        return pixel_per_cm
    else:
        return None

def segment_food(image):
    results = model(image)
    masks = results[0].masks
    boxes = results[0].boxes

    if masks is None:
        return None, None

    food_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    food_class = None
    food_bbox = None

    for i, mask in enumerate(masks.data):
        mask_np = mask.cpu().numpy().astype(np.uint8) * 255
        mask_resized = cv2.resize(mask_np, (image.shape[1], image.shape[0]))
        food_mask = cv2.bitwise_or(food_mask, mask_resized)

        food_class = results[0].names[int(boxes.cls[i])]
        food_bbox = boxes.xyxy[i].cpu().numpy()  # Bounding box [x1, y1, x2, y2]
    
    return food_mask, food_class, food_bbox

def calculate_real_area(food_mask, pixel_per_cm):
    pixel_area = np.sum(food_mask > 0)
    return pixel_area / (pixel_per_cm ** 2)

def calculate_width_length(bbox, pixel_per_cm):
    x1, y1, x2, y2 = bbox
    width = abs(x2 - x1) / pixel_per_cm
    length = abs(y2 - y1) / pixel_per_cm
    return width, length

def calculate_shape_features(food_mask):
    contours, _ = cv2.findContours(food_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return [0] * 6
    cnt = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(cnt)
    perimeter = cv2.arcLength(cnt, True)
    x, y, w, h = cv2.boundingRect(cnt)
    aspect_ratio = w / h if h else 0
    extent = area / (w * h) if (w * h) else 0
    hull_area = cv2.contourArea(cv2.convexHull(cnt))
    solidity = area / hull_area if hull_area else 0
    circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter else 0
    return aspect_ratio, extent, solidity, circularity, area, perimeter

def estimate_volume(width, length):
    return (4/3) * np.pi * (width/2) * (length/2) * (min(width, length)/2)

def extract_color_features(image, food_mask):
    masked = cv2.bitwise_and(image, image, mask=food_mask)
    return cv2.mean(masked, mask=food_mask)[:3]

def compute_edge_density(food_mask):
    edges = cv2.Canny(food_mask, 100, 200)
    return np.sum(edges) / np.sum(food_mask > 0) if np.sum(food_mask > 0) else 0

def extract_features_from_image(image):
    # Convert to BGR if input is from PIL (e.g., Streamlit)
    if image.shape[-1] == 4:  # RGBA
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    elif image.shape[-1] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    pixel_per_cm = detect_aruco_marker(image)
    if pixel_per_cm is None:
        raise ValueError("ArUco marker not found.")

    food_mask, food_type, food_bbox = segment_food(image)
    if food_mask is None or food_bbox is None:
        raise ValueError("Food not detected.")

    food_area = calculate_real_area(food_mask, pixel_per_cm)
    food_width, food_length = calculate_width_length(food_bbox, pixel_per_cm)
    aspect_ratio, extent, solidity, circularity, contour_area, perimeter = calculate_shape_features(food_mask)
    volume = estimate_volume(food_width, food_length)
    mean_r, mean_g, mean_b = extract_color_features(image, food_mask)
    edge_density = compute_edge_density(food_mask)

    # Encode food_type using OneHotEncoder
    food_encoded = encoder.transform([[food_type]])[0].tolist()
    food_class_columns = encoder.get_feature_names_out(['Food_type'])

    # Create feature vector
    features = [
        pixel_per_cm, food_area, food_width, food_length,
        aspect_ratio, extent, solidity, circularity, volume,
        mean_r, mean_g, mean_b, edge_density
    ] + food_encoded 

    columns =  [
        "Pixels_per_cm", "Food_area", "Food_width", "Food_length",
        "Aspect_Ratio", "Extent", "Solidity", "Circularity", "Estimated_Volume",
        "Mean_R", "Mean_G", "Mean_B", "Edge_Density"
    ] + list(food_class_columns)

    return food_type, pd.DataFrame([features], columns=columns)
