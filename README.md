# Machine Learning-based Algorithm for Malaysian Food Image Recognition and Calories Prediction

## Overview
This project focuses on building a **machine learning-based system** for **Malaysian food image recognition** and **calorie prediction**.  
The system integrates **YOLOv11 instance segmentation** for food recognition with regression models for food weight estimation, followed by calorie calculation using a **custom Malaysian Food Composition Database API**.

The motivation comes from the lack of standardized Malaysian food datasets and the limitations of traditional weight estimation methods. This project provides a practical solution for accurate calorie prediction from a single food image.

---

## Methodology
- **Food Recognition**
  - Trained a **YOLOv11 instance segmentation model** on a custom dataset of Malaysian foods.
  - Achieved robust detection and segmentation across 10 food categories.

- **Food Weight Estimation**
  - Evaluated three gradient boosting algorithms: **XGBoost**, **CatBoost**, and **LightGBM**.
  - Compared performance using **Mean Absolute Error (MAE)** and **Mean Absolute Percentage Error (MAPE)**.
  - Developed an alternative **multi-task YOLOv11 regression head** to jointly perform recognition and weight estimation.

- **Calorie Prediction**
  - Created a **Malaysian Food Composition Database API** using FastAPI.
  - The API retrieves nutritional information (calories, protein, fat, carbohydrates) based on food type and estimated weight.

---

## Results

### Food Recognition
- **YOLOv11 instance segmentation** achieved **99.99% precision** and **100% recall**, demonstrating highly accurate Malaysian food detection.

### Weight Estimation
- **XGBoost** performed best with a **Mean Absolute Error (MAE) of 6.67g**.
- **CatBoost** and **LightGBM** also gave competitive results but were slightly less accurate.
- The **multi-task YOLOv11 regression head** showed feasibility for end-to-end learning but was outperformed by the separated XGBoost model.

### Calorie Prediction Application
- The integrated system successfully combined recognition, weight estimation, and the nutritional database to deliver **accurate calorie predictions**.
- Enabled automated calorie estimation from a **single image input**, improving over manual or serving-size–based methods.

---

## Conclusion
This project demonstrates that combining **YOLOv11** for food recognition and **XGBoost** for weight estimation provides an effective solution for **Malaysian food calorie prediction**.  
The system has potential applications in **diet monitoring, healthcare, and nutrition management** in Malaysia.

