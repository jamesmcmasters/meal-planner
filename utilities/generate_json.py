import random
from datetime import datetime
import os
import re
import json

current_date = datetime.now().strftime('%Y-%m-%d')
filepath = r'/mnt/c/users/lenovo/documents/notes/notes/areas/meal plans'
THUMBNAIL_DIR = "images"
RECIPE_FILE = "recipes.txt"
OUTPUT_FILE = "recipes.json"

# Conversion factors for alternate units (simplified)
CONVERSIONS = {
    "g": {
        "tsp": 0.2,   # 1g = 0.2 tsp
        "tbsp": 0.067, # 1g = 0.067 tbsp
        "oz": 0.035274, # 1g = 0.035274 oz
        "lbs": 0.00220462 # 1g = 0.00220462 lbs
    },
    "tbsp": {
        "g":14.79,
    },
    "oz": {
        "g":28.3495,
    },
}

def convert_units(quantity, from_unit, to_unit):
    """ Convert quantity from one unit to another based on available conversion data. """
    if from_unit == to_unit:
        return quantity
    if from_unit in CONVERSIONS and to_unit in CONVERSIONS[from_unit]:
        return quantity * CONVERSIONS[from_unit][to_unit]
    return None

def normalize_name(name):
    name = name.split('-')[0].replace('&','').strip().lower()
    name = re.sub(r'\s+', '_', name)
    return name

def read_meals_from_file(file_name=RECIPE_FILE):
    meals = {}

    with open(file_name, 'r') as file:
        lines = file.readlines()

        current_meal = None
        current_recipe_url = None
        ingredients = []
        thumbnail = None

        for line in lines:
            line = line.strip()

            if line == "":
                continue

            # MEAL NAME
            if line.isupper():
                if current_meal:
                    meals[current_meal] = {
                        "url": current_recipe_url,
                        "ingredients": ingredients,
                        "thumbnail": thumbnail
                    }
                current_meal = line.title()
                thumbnail = f"{normalize_name(line)}.png" #Assuming jpg
                print(thumbnail)
                if os.path.exists(os.path.join(THUMBNAIL_DIR,thumbnail)):
                    thumbnail = f"{THUMBNAIL_DIR}/{thumbnail}"
                else:
                    thumbnail = f"{THUMBNAIL_DIR}/placeholder.png"
                ingredients = []

            # RECIPE URL
            elif line.startswith("http"):
                current_recipe_url = line

            # INGREDIENTS (formatted like: X | unit | item or || item)
            else:
                parts = line.split("|")
                if len(parts) == 3:  # Format: X | unit | item
                    quantity = parts[0].strip()
                    unit = parts[1].strip()
                    item = parts[2].strip()

                    if quantity:
                        quantity = float(quantity)
                    else:
                        quantity = 1  # No quantity specified

                    if unit in ["tbsp", "oz"]:
                        quantity = convert_units(quantity, unit, "g")
                        unit = "g"

                    ingredients.append({
                        "quantity": quantity,
                        "unit": unit,
                        "item": item
                    })
                elif len(parts) == 2 and parts[0].strip() == "":  # Format: || item
                    item = parts[1].strip()
                    ingredients.append({
                        "quantity": 1,
                        "unit": "",
                        "item": item
                    })
                elif len(parts) == 2 and parts[1].strip() == "":  # Format: X || item
                    quantity = parts[0].strip()
                    item = parts[1].strip()
                    ingredients.append({
                        "quantity": float(quantity),
                        "unit": "",
                        "item": item
                    })
        
        # Add the last meal
        if current_meal:
            meals[current_meal] = {
                "url": current_recipe_url,
                "ingredients": ingredients,
                "thumbnail": thumbnail
            }

    return meals

data = read_meals_from_file()
with open(OUTPUT_FILE, "w") as out:
    json.dump(data,out,indent=2)
print(f"Wrote {len(data)} recipes to {OUTPUT_FILE}")

