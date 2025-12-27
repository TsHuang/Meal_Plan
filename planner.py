import csv
import random
from collections import defaultdict, Counter
import pandas as pd

class Dish:
    def __init__(self, name, category, ingredients):
        self.name = name
        self.category = category  # 'Protein', 'Egg', 'Other'
        self.ingredients = [i.strip() for i in ingredients.split(',') if i.strip()]

    def __repr__(self):
        return f"{self.name} ({self.category})"

class MealPlanner:
    def __init__(self, dishes):
        self.dishes = dishes
        self.by_category = defaultdict(list)
        for d in dishes:
            self.by_category[d.category].append(d)
        
        # Verify we have enough data
        self.categories = ['Protein', 'Egg', 'Other']
        for cat in self.categories:
            if not self.by_category[cat]:
                print(f"Warning: No dishes found for category '{cat}'")

    def generate_meal(self, n=4):
        """
        Generates a single meal (Lunch or Dinner) with n dishes.
        Attempts to include variety. 
        Note constraints: "Daily" needs all 3 categories. 
        This function just picks n dishes, we'll validate daily constraints later or build carefully.
        
        To simplify 'Daily' constraint (Protein, Egg, Other):
        We can try to ensure each MEAL has variety, or just check the day.
        Let's try to make each meal balanced if possible, ensuring at least one of each if n >= 3.
        """
        meal = []
        # Mandatory categories for a balanced meal (soft constraint, but good for "Daily" check)
        # If we have 4 dishes, we can pick 1 Protein, 1 Egg, 1 Other, and 1 Random.
        
        pool = self.dishes[:]
        random.shuffle(pool)
        
        chosen_cats = set()
        
        # Try to pick one from each category first
        for cat in self.categories:
            options = [d for d in pool if d.category == cat and d not in meal]
            if options:
                selection = random.choice(options)
                meal.append(selection)
                chosen_cats.add(cat)
        
        # Fill the rest
        while len(meal) < n:
            remaining = [d for d in pool if d not in meal]
            if not remaining:
                break # Ran out of dishes
            meal.append(random.choice(remaining))
            
        return meal

    def generate_day(self):
        # Generate Lunch and Dinner
        # Constraint: Daily must have Protein, Egg, Other.
        # Since our generate_meal tries to include all 3, this is likely satisfied.
        # We also want to avoid repeating dishes between Lunch and Dinner on the same day.
        
        lunch = self.generate_meal(4)
        
        # Filter out lunch dishes for dinner to ensure daily variety
        dinner_pool = [d for d in self.dishes if d not in lunch]
        
        # Custom generate for dinner using filtered pool
        dinner = []
        temp_planner = MealPlanner(dinner_pool) # Create a temp planner with reduced pool
        dinner = temp_planner.generate_meal(4)
        
        return lunch, dinner

    def generate_month_plan(self, days=28):
        plan = []
        for day_num in range(1, days + 1):
            lunch, dinner = self.generate_day()
            
            # Record the day's plan
            day_data = {
                'Day': day_num,
                'Lunch': [d.name for d in lunch],
                'Dinner': [d.name for d in dinner],
                'Lunch_Objects': lunch,
                'Dinner_Objects': dinner
            }
            plan.append(day_data)
        return plan

    def aggregate_ingredients(self, plan):
        # Weekly aggregation
        # Returns a dict: Week Num -> Counter of ingredients
        shopping_lists = {}
        
        for i, day in enumerate(plan):
            week_num = (i // 7) + 1
            if week_num not in shopping_lists:
                shopping_lists[week_num] = Counter()
            
            all_dishes = day['Lunch_Objects'] + day['Dinner_Objects']
            for dish in all_dishes:
                for ing in dish.ingredients:
                    shopping_lists[week_num][ing] += 1
                    
        return shopping_lists

def load_dishes_from_csv(filepath):
    dishes = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle potential key case sensitivity or whitespace
                name = row.get('Dish Name') or row.get('name')
                cat = row.get('Category') or row.get('category')
                ings = row.get('Ingredients') or row.get('ingredients')
                
                if name and cat:
                    dishes.append(Dish(name, cat, ings if ings else ""))
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []
    return dishes

def save_plan_to_csv(plan, filename="meal_plan.csv"):
    # Flatten for CSV
    # Day, Meal, Dish 1, Dish 2, Dish 3, Dish 4
    rows = []
    for day in plan:
        # Lunch
        row_l = {'Day': day['Day'], 'Meal': 'Lunch'}
        for i, d in enumerate(day['Lunch']):
            row_l[f'Dish {i+1}'] = d
        rows.append(row_l)
        
        # Dinner
        row_d = {'Day': day['Day'], 'Meal': 'Dinner'}
        for i, d in enumerate(day['Dinner']):
            row_d[f'Dish {i+1}'] = d
        rows.append(row_d)
        
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"Plan saved to {filename}")

def save_shopping_list(shopping_lists, filename="shopping_list.csv"):
    rows = []
    for week, counter in shopping_lists.items():
        for ingredient, count in counter.items():
            rows.append({
                'Week': week,
                'Ingredient': ingredient,
                'Count': count
            })
            
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"Shopping list saved to {filename}")

if __name__ == "__main__":
    # Test Run
    dishes = load_dishes_from_csv("dishes.csv")
    if not dishes:
        print("No dishes loaded. Please check dishes.csv")
    else:
        print(f"Loaded {len(dishes)} dishes.")
        planner = MealPlanner(dishes)
        plan = planner.generate_month_plan()
        save_plan_to_csv(plan)
        
        shopping = planner.aggregate_ingredients(plan)
        save_shopping_list(shopping)
