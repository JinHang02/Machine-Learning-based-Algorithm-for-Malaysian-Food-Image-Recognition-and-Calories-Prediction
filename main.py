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

# @app.get("/calories")
# async def get_calories(food: str = Query(..., description="The name of the food"), 
#                        weight: float = Query(..., description="Weight of the food in grams")):
#     """
#     Endpoint to calculate calories based on food name and weight.
    
#     Parameters:
#     - food: Name of the food (string).
#     - weight: Weight of the food in grams (float).

#     Returns:
#     - JSON response with the calculated calories.
#     """
#     try:
#         # Load the data from the Excel file
#         df = pd.read_excel(EXCEL_FILE_PATH)
#         df = df.fillna(0)

#         # Normalize food names in the DataFrame and input for case-insensitivity
#         df["Food"] = df["Food"].str.strip().str.lower()
#         food = food.strip().lower()

#         # Check if the food exists in the dataset
#         if food not in df["Food"].values:
#             raise HTTPException(status_code=404, detail=f"Food '{food}' not found in the database.")

#         # Get the row corresponding to the food
#         food_data = df[df["Food"] == food].iloc[0]

#         # Extract weight and calories from the dataset
#         dataset_weight = food_data["Weight"]
#         dataset_calories = food_data["Calories"]

#         # Calculate the calories based on the input weight
#         calculated_calories = (weight / dataset_weight) * dataset_calories

#         # Return the calculated calories
#         return {
#             "food": food_data["Food"],
#             "input_weight": weight,
#             "calculated_calories": int(calculated_calories)
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/nutrient")
async def get_nutrient(
    food: str = Query(..., description="The name of the food"),
    weight: float = Query(..., description="Weight of the food in grams"),
    nutrient: str = Query(..., description="Nutrient to retrieve (Calories, Carbohydrate, Protein, Fat)")
):
    """
    Endpoint to calculate the requested nutrient (Calories, Carbohydrate, Protein, or Fat)
    based on food name and weight.
    
    Parameters:
    - food: Name of the food (string).
    - weight: Weight of the food in grams (float).
    - nutrient: The specific nutrient to calculate (Calories, Carbohydrate, Protein, or Fat).

    Returns:
    - JSON response with the calculated nutrient value.
    """
    try:
        # Load data
        df = pd.read_excel(EXCEL_FILE_PATH)
        df = df.fillna(0)

        # Normalize food names
        df["Food"] = df["Food"].str.strip().str.lower()
        food = food.strip().lower()

        # Validate food name
        if food not in df["Food"].values:
            raise HTTPException(status_code=404, detail=f"Food '{food}' not found in the database.")

        # Validate nutrient
        valid_nutrients = ["Calories", "Carbohydrate", "Protein", "Fat"]
        if nutrient not in valid_nutrients:
            raise HTTPException(status_code=400, detail=f"Invalid nutrient. Choose from: {', '.join(valid_nutrients)}")

        # Get the food data
        food_data = df[df["Food"] == food].iloc[0]

        # Extract weight and requested nutrient value
        dataset_weight = food_data["Weight"]
        dataset_nutrient_value = food_data[nutrient]

        # Calculate the proportional nutrient value
        calculated_value = (weight / dataset_weight) * dataset_nutrient_value

        return {
            "food": food_data["Food"],
            "input_weight": weight,
            "requested_nutrient": nutrient,
            "calculated_value": round(calculated_value, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")