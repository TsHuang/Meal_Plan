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
        self.categories = ['Protein', 'Egg', 'Vegetable', 'Other']
        for cat in self.categories:
            if not self.by_category[cat]:
                print(f"Warning: No dishes found for category '{cat}'")
                
        # Staple Logic
        self.staples = ['Rice', 'Noodle', 'Combo (Rice)', 'Combo (Noodle)']
        self.last_noodle_date = None # Track last date noodles were used

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

    def get_daily_staple(self, current_date, is_egg_day):
        import datetime
        
        # Determine available options
        options = []
        
        # Check noodle constraint (once every 14 days)
        can_have_noodle = False
        if self.last_noodle_date is None:
            can_have_noodle = True
        elif (current_date - self.last_noodle_date).days >= 14:
            can_have_noodle = True
            
        # Filter Staples
        # On Non-Egg days, we force FORCE normal staples (Rice/Noodle) because we need 4 slots.
        # (User rule: Non-Egg = P + V + 2Other = 4 dishes). 
        # Combo only allows 3 dishes, so Combo is incompatible with Non-Egg day.
        
        allowed_types = self.staples[:]
        if not is_egg_day:
            # Must be Normal
            allowed_types = [s for s in allowed_types if 'Combo' not in s]
        
        if can_have_noodle:
            options = allowed_types
        else:
            # Filter out Noodle types
            options = [s for s in allowed_types if 'Noodle' not in s]
            
        # Select one
        if not options:
            # Fallback if over-constrained (shouldn't happen with Rice)
            return 'Rice'
            
        selected = random.choice(options)
        
        # Update tracker
        if 'Noodle' in selected:
            self.last_noodle_date = current_date
            
        return selected

    def generate_dinner(self, staple, is_egg_day):
        # Determine dish count based on Staple
        # Combo -> 3 dishes
        # Normal -> 4 dishes
        n_dishes = 4
        if 'Combo' in staple:
            n_dishes = 3
            
        # Strict Composition Rules
        # Egg Day (3/week): 1 Protein + 1 Veg + 1 Egg (+1 Random if n=4)
        # Non-Egg Day (2/week): 1 Protein + 1 Veg + 2 Other (Total 4) -> Must be Normal staple
        
        meal = []
        
        # 1. Mandatory Protein
        p_options = self.by_category['Protein']
        if p_options:
            meal.append(random.choice(p_options))
            
        # 2. Mandatory Vegetable (User said "Vegetable", distinct from Other)
        v_options = self.by_category['Vegetable']
        if v_options:
            meal.append(random.choice(v_options))
            
        # 3. Conditional Rules
        if is_egg_day:
            # Must have Egg
            e_options = self.by_category['Egg']
            if e_options:
                meal.append(random.choice(e_options))
        else:
            # Non-Egg Day -> 2 Others
            # We already used 2 slots (P+V). We need 2 Others. 
            o_options = self.by_category['Other']
            # Pick 2 distinct if possible
            if len(o_options) >= 2:
                meal.extend(random.sample(o_options, 2))
            else:
                # Fallback if not enough other
                meal.extend(o_options)
        
        # 4. Fill Remaining Slots (if any)
        # For Egg Day with Normal Staple (n=4), we have P+V+E (3 items). Need 1 more.
        # For Non-Egg Day with Normal Staple (n=4), we have P+V+2O (4 items). Full.
        
        while len(meal) < n_dishes:
            # Pick random from Protein or Vegetable (avoid egg if strict non-egg, avoid too many others)
            pool = self.by_category['Protein'] + self.by_category['Vegetable']
            remaining_pool = [d for d in pool if d not in meal]
            if remaining_pool:
                meal.append(random.choice(remaining_pool))
            else:
                break
                
        return meal

    def generate_month_plan(self, days=28, start_date=None):
        import datetime
        
        if start_date is None:
            start_date = datetime.date.today()
            
        plan = []
        
        # We process week by week to enforce the "3 Egg Days per Week" rule
        # A week is defined as Mon-Sun? Or just chunks of 5 weekdays?
        # Let's assume chunks of 5 weekdays for the "per week" rule.
        
        # But generate_month_plan iterates day by day.
        # We can pre-calculate egg status.
        
        # Create a map for dates
        egg_schedule = {} # date_str -> bool
        
        current_processing_date = start_date
        total_processed = 0
        while total_processed < days:
             # Find the Monday of the current week (or just current chunk)
             # Actually, simpler: verify if it's a weekday.
             # If we want "One week has 3 egg days", we should look at ISO weeks or just rolling 5 days.
             # Let's do ISO weeks (Mon-Sun).
             
             year, week, weekday = current_processing_date.isocalendar()
             week_key = (year, week)
             
             # If we haven't planned this week yet
             # Get all weekdays for this week
             week_start = current_processing_date - datetime.timedelta(days=weekday-1)
             week_days = []
             for i in range(5): # Mon(0) to Fri(4)
                 d = week_start + datetime.timedelta(days=i)
                 if d >= start_date:
                     week_days.append(d)
             
             # Randomly pick 3 days to be Egg Days (if we have enough days)
             # If we have fewer than 3 days in this partial week, make them all egg days?
             count = len(week_days)
             egg_count = min(3, count)
             
             # If full week (5 days), picked 3.
             # We need to be careful not to re-plan.
             
             # Let's just iterate through the requested duration.
             # When we hit a Monday (or start), plan the whole week's egg schedule?
             pass 
             total_processed += 1 # Just loop logic holder
             current_processing_date += datetime.timedelta(days=1)

        # Better approach: Iterate days, group by Week
        from collections import defaultdict
        week_groups = defaultdict(list)
        
        for day_num in range(days):
            d = start_date + datetime.timedelta(days=day_num)
            if d.weekday() < 5: # Mon-Fri
                iso_year, iso_week, _ = d.isocalendar()
                week_groups[(iso_year, iso_week)].append(d)
        
        # Assign egg days
        egg_flags = {}
        for wk, dates in week_groups.items():
            # Pick 3 days to be Egg
            k = min(3, len(dates))
            egg_dates = set(random.sample(dates, k))
            for d in dates:
                egg_flags[d] = (d in egg_dates)
        
        # Generate Logic
        for day_num in range(days):
            current_date = start_date + datetime.timedelta(days=day_num)
            
            # Weekday check: 0=Mon, 4=Fri, 5=Sat, 6=Sun
            if current_date.weekday() >= 5:
                # Weekend - No meals
                dinner = []
                daily_staple = "None"
            else:
                is_egg = egg_flags.get(current_date, False)
                daily_staple_cat = self.get_daily_staple(current_date, is_egg)
                
                # Always pick a specific dish name from the category
                # This covers Rice, Noodle, Combo (Rice), Combo (Noodle)
                staple_dishes = self.by_category.get(daily_staple_cat, [])
                if staple_dishes:
                    selected_staple = random.choice(staple_dishes)
                    daily_staple_display = selected_staple.name
                else:
                    # Fallback if no specific dishes defined for this category
                    daily_staple_display = daily_staple_cat

                dinner = self.generate_dinner(daily_staple_cat, is_egg)
            
            # Record the day's plan
            day_data = {
                'Day': day_num + 1,
                'Date': current_date, # Date object
                'DateStr': current_date.strftime("%Y-%m-%d"),
                'Weekday': current_date.strftime("%a"), # Mon, Tue...
                'Staple': daily_staple_display,
                'Dinner': [d.name for d in dinner],
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
            
            all_dishes = day['Dinner_Objects']
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
        # Dinner Only
        row_d = {
            'Day': day['Day'], 
            'Date': day['DateStr'], 
            'Weekday': day['Weekday'], 
            'Staple': day['Staple'],
            # 'Meal': 'Dinner' # Redundant if only one meal
        }
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
