import requests

# Define the API endpoint URL
API_URL = "http://127.0.0.1:8000/nutrient"

while True:
    try:
        food = str(input("Name of Food:"))
        weight = float(input("Weight of Food:"))

        if food is not None and weight is not None:
            params = {
                "food": food,
                "weight": weight
            }
            break
    except:
        print("Incorrect Input")

# Make a GET request to the endpoint
try:
    response = requests.get(API_URL, params=params)
    # Print the response JSON if the request was successful
    print(f"Response: \n{response.json()}")
except Exception as err:
    print(f"Error occurred: {err}")