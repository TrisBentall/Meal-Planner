import json
import os
import random

from datetime import datetime, timedelta

recipes_file_path = 'recipes.json'
pantry_file_path = 'pantry.json'
previous_meals_file_path = 'previous_meals.json'

# Load in the json databases

def load_recipes(recipes_file_path):
    with open(recipes_file_path, 'r') as recipe_file:
        recipes = json.load(recipe_file)
    return recipes

def load_pantry(pantry_file_path):
    with open(pantry_file_path, 'r') as pantry_file:
        pantry = json.load(pantry_file)
    return pantry

def load_previous_meals(previous_meals_file_path):
    with open(previous_meals_file_path, 'r') as previous_meals_file:
        previous_meals = json.load(previous_meals_file)
    return previous_meals

def save_previous_meals(previous_meals_file_path, previous_meals):
    with open(previous_meals_file_path, 'w') as file:
        json.dump(previous_meals, file)

def calculate_freshness(ingredient, pantry):
    if ingredient['name'] in pantry and 'expiry_date' in pantry[ingredient['name']]:
        expiry_date = datetime.strptime(pantry[ingredient['name']]['expiry_date'], "%Y-%m-%d")
        days_until_expiry = (expiry_date - datetime.now()).days

        freshness_factor = max(0, min(1, days_until_expiry / 7))
        return freshness_factor
    else:
        return 1 # No freshness data

def choose_meals(recipes, pantry, previous_meals):
    chosen_meals = []
    current_meals = []

    if not isinstance(previous_meals, list):
        previous_meals = []

    for _ in range(3): # Choose meals for each day of the week
        # Filter out meals from previous week
        available_recipes = [recipe for recipe in recipes if recipe['name'] not in (previous_meals + current_meals)]

        # Calculate freshness factors for available ingredients
        freshness_factors = [sum(calculate_freshness(ingredient, pantry) for ingredient in meal['ingredients']) for meal in available_recipes]

        # Adjust probabilities based on freshness factors
        total_freshness = sum(freshness_factors)
        probabilities = [factor / total_freshness for factor in freshness_factors]

        if not available_recipes:
            break # No suitabl meal found for the remaining days

        chosen_meal = random.choices(available_recipes, probabilities)[0]
        
        while chosen_meals and any(tag in chosen_meal.get('tags', []) for tag in chosen_meals[-1].get('tags', [])):
            chosen_meal = random.choices(available_recipes, probabilities)[0]
        
        chosen_meals.append(chosen_meal)

        # Log the chosen meal
        current_meals.append(chosen_meal['name'])
    # Remove the previous weeks meals from the database
    updated_previous_meals = [meal for meal in (previous_meals + current_meals) if meal in current_meals]

    return chosen_meals, updated_previous_meals

def main():
    recipes = load_recipes(recipes_file_path)
    pantry = load_pantry(pantry_file_path)
    previous_meals = load_previous_meals(previous_meals_file_path)

    chosen_meals, updated_previous_meals = choose_meals(recipes, pantry, previous_meals)

    if choose_meals:
        for day, meal in enumerate(chosen_meals, start=1):
            print(f"Day {day}: {meal['name']}")
            print(f"Ingredients: {', '.join(ingredient['name'] for ingredient in meal['ingredients'])}")
            print()
        
        # Update the previous_meals database
        save_previous_meals(previous_meals_file_path, updated_previous_meals)
        print("Meals saved")

    else:
        print("No suitable meals found based on the available ingredients and previous week's meals.")

if __name__ == "__main__":
    main()
