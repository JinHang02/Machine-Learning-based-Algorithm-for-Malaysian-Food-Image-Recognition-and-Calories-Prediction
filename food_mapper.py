# Left = food name detected by YOLO
# right = food name in API
FOOD_NAME_MAPPING = {
    "apple": "gala apple",
    "banana": "banana",
    "tangerine": "tangerine",
    "fried noodle": "noodle, rice",
    "fried rice": "rice, fried",
    "rojak": "rojak",
    "cooked rice": "rice, cooked",
    "oat": "oats, rolled",
    "mashed potato": "potato, mashed",
    "coleslaw": "coleslaw"
}

def map_to_api_name(local_food_name: str) -> str:
    """
    Maps internal/local food name to the name expected by the API.

    Parameters:
        local_food_name (str): Food name predicted or used locally

    Returns:
        str: Corresponding food name used in the API
    """
    return FOOD_NAME_MAPPING.get(local_food_name.lower(), "Unknown Food")