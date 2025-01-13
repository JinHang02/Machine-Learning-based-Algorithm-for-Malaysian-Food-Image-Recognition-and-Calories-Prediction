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

@app.get("/calories")
async def get_calories(food: str = Query(..., description="The name of the food"), 
                       weight: float = Query(..., description="Weight of the food in grams")):
    """
    Endpoint to calculate calories based on food name and weight.
    
    Parameters:
    - food: Name of the food (string).
    - weight: Weight of the food in grams (float).

    Returns:
    - JSON response with the calculated calories.
    """
    try:
        # Load the data from the Excel file
        df = pd.read_excel(EXCEL_FILE_PATH)
        df = df.fillna(0)

        # Normalize food names in the DataFrame and input for case-insensitivity
        df["Food"] = df["Food"].str.strip().str.lower()
        food = food.strip().lower()

        # Check if the food exists in the dataset
        if food not in df["Food"].values:
            raise HTTPException(status_code=404, detail=f"Food '{food}' not found in the database.")

        # Get the row corresponding to the food
        food_data = df[df["Food"] == food].iloc[0]

        # Extract weight and calories from the dataset
        dataset_weight = food_data["Weight"]
        dataset_calories = food_data["Calories"]

        # Calculate the calories based on the input weight
        calculated_calories = (weight / dataset_weight) * dataset_calories

        # Return the calculated calories
        return {
            "food": food_data["Food"],
            "input_weight": weight,
            "calculated_calories": int(calculated_calories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# @app.post("/update")
# async def update_data(request: Request):
#     """
#     Endpoint to update data in the Excel file.
#     Expects JSON input with the new data.
#     """
#     try:
#         # Get the data from the request
#         new_data = await request.json()

#         # Convert JSON to DataFrame
#         df = pd.DataFrame(new_data)

#         # Save the DataFrame to the Excel file
#         df.to_excel(EXCEL_FILE_PATH, index=False)

#         return {"message": "Data updated successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error updating Excel file: {str(e)}")