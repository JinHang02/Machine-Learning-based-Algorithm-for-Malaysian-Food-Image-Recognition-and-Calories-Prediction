# streamlit run app.py
import requests
import streamlit as st
import numpy as np
import pandas as pd
import xgboost as xgb
from PIL import Image
from features import extract_features_from_image  
from food_mapper import map_to_api_name

# Load trained XGBoost model
xgb_model = xgb.XGBRegressor()
xgb_model.load_model("./xgboost/xgboost_model.json")  # Update path accordingly

# Streamlit app
st.set_page_config(page_title="Food Nutrition Retrieval Application", layout="wide")
st.title("NutriVision")
# st.title("🍱 Automated Calories Prediction Application")
# st.title("🍱 Food Nutrition Retrieval Application")


# Upload image
uploaded_file = st.file_uploader("Upload a food image with ArUco marker", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    img_np = np.array(image)

    # Create two columns: image (left), info (right)
    col1, col2 = st.columns([1.2, 1.8])

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:
        try:
            # Extract features using your custom pipeline
            food_type, features_df = extract_features_from_image(img_np)

            # Display extracted features
            with st.expander("🔍 **Extracted Features**"):
                st.dataframe(features_df, hide_index = True)

            # Predict weight
            predicted_weight = xgb_model.predict(features_df)[0]

            if food_type and predicted_weight:
                st.subheader("📌 Predicted Food Type & Weight")
                st.markdown(f"<span style='font-size:18px'>🍱 <b>Food Type:</b> {food_type}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='font-size:18px'>⚖️ <b>Food Weight:</b> {predicted_weight:.2f} grams</span>", unsafe_allow_html=True)

                # --- CALL FASTAPI /nutrient API ---
                st.subheader("🔬 Food Nutrient Information Estimation")

                api_food_type = map_to_api_name(food_type)
                api_url = "http://localhost:8000/nutrient"
                params = {"food": api_food_type, "weight": predicted_weight}
                response = requests.get(api_url, params=params)

                if response.status_code == 200:
                    nutrient_data = response.json()
                    st.success(f"Nutrient information for **{predicted_weight:.2f}g** of **{food_type}**:")

                    nutrient_table = nutrient_data["calculated_nutrients"]
                    # print nutrient table
                    st.dataframe(pd.DataFrame(nutrient_table.items(), columns=["Nutrient", "Amount"]), hide_index = True)
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
            else:
                st.error("❌ Food in image is not detected in database.")

        except ValueError as e:
            st.error(f"❌ {str(e)}")
