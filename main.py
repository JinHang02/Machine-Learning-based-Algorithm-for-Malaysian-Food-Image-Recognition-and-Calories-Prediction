#  uvicorn main:app --reload

from fastapi import FastAPI, HTTPException, Query
import pandas as pd

# Initialize FastAPI app
app = FastAPI()

# Path to your Excel file
EXCEL_FILE_PATH = "./food-dataset.xlsx"

@app.get("/data")
async def get_data():
    """
    Endpoint to fetch data from the Excel file.
    """
    try:
        # Load data from the Excel file
        df = pd.read_excel(EXCEL_FILE_PATH)
        df = df.fillna(0)
        data = df.to_dict(orient="records")
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading Excel file: {str(e)}")

@app.get("/nutrient")
async def get_nutrient(
    food: str = Query(..., description="The name of the food"),
    weight: float = Query(..., description="Weight of the food in grams")
):
    """
    Endpoint to calculate all nutrients (Calories, Carbohydrate, Protein, and Fat)
    based on food name and weight.
    
    Parameters:
    - food: Name of the food (string).
    - weight: Weight of the food in grams (float).

    Returns:
    - JSON response with all calculated nutrient values.
    """
    try:
        # Load data
        df = pd.read_excel(EXCEL_FILE_PATH)
        df = df.fillna(0)

        # Normalize and split food names into Malay and English
        df["Malay_Name"] = df["Food"].str.extract(r"^([^(]+)").iloc[:, 0].str.strip().str.lower()
        df["English_Name"] = df["Food"].str.extract(r"\(([^)]+)\)").iloc[:, 0].str.strip().str.lower()

        # Normalize input
        food = food.strip().lower()

        # Try to match either Malay or English name
        matched_row = df[(df["Malay_Name"] == food) | (df["English_Name"] == food)]

        if matched_row.empty:
            raise HTTPException(status_code=404, detail=f"Food '{food}' not found in the database.")

        food_data = matched_row.iloc[0]

        # Extract weight and nutrient values
        dataset_weight = food_data["Weight"]
        nutrients = ["Calories", "Carbohydrate", "Protein", "Fat","Calcium","Iron","Sodium","Potassium","Vitamin C","Cholesterol"]

        calculated_nutrients = {}
        for nutrient in nutrients:
            value = round((weight / dataset_weight) * food_data[nutrient], 2)
            unit = "mg" if nutrient in ["Vitamin C", "Cholesterol"] else "g"
            calculated_nutrients[nutrient] = f"{value} {unit}"

        return {
            "food": food_data["Food"],
            "input_weight": weight,
            "calculated_nutrients": calculated_nutrients
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")