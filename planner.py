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
        self.staples = ['Rice', 'Combo (Rice)', 'Combo (Noodle)']
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

    def get_daily_staple(self, current_date, is_egg_day, last_combo_date=None):
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
            
        if allowed_types: # Optimization
            days_since_combo = 999
            if last_combo_date:
                days_since_combo = (current_date - last_combo_date).days
                
            if days_since_combo <= 2:
                # Disperse rule: At least 2 days gap (e.g. Mon->Thu)
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

    def identify_meat_type(self, dish_name):
        name = dish_name.lower()
        if '魚' in name and '吻仔魚' not in name: return 'Fish' # Main fish dishes
        if '吻仔魚' in name: return 'Fish' # Treat as fish
        if '牛' in name: return 'Beef'
        if '豬' in name: return 'Pork'
        if '雞' in name and '雞蛋' not in name and '蛋' not in name: return 'Chicken' # Avoid Egg matches
        if '雞肉' in name: return 'Chicken'
        if '蝦' in name: return 'Shrimp'
        if '蛤蜊' in name: return 'Clam'
        return None

    def generate_dinner(self, staple, is_egg_day, weekly_used_dishes, weekly_fish_count):
        # Determine dish count
        # Combo -> 3 items (Staple + 2 sides)
        # Normal -> 4 items (Staple + 3 sides - Wait, normal is 4 dishes total including staple?)
        # Let's check CSV output. Only Side dishes are in 'Dinner_Objects'.
        # Previous layout: Staple is separate.
        # Logic: 
        # Egg Day (Normal): 1P + 1V + 1E. (3 sides).
        # Non-Egg (Normal): 1P + 1V + 2B. (4 sides).
        # Combo: "配菜就不安排蛋白質". 
        #   Egg Day (Combo): 0P + 1V + 1E. (2 sides).
        #   Non-Egg (Combo): N/A (Combo not allowed).
        
        target_sides = 4 # Default for Normal Staple
        if 'Combo' in staple:
            target_sides = 2 # 1V + 1E (Protein excluded, Veg included, Egg included)
            
        meal = []
        daily_meats = set()
        
        # Helper to pick form list
        def pick_valid(category, pool, count=1, exclude_meat_types=None):
            # Filter by weekly used
            candidates = [d for d in pool if d.name not in weekly_used_dishes and d not in meal]
            
            # Filter by constraints
            valid = []
            for d in candidates:
                # Vegetable Limit: If we already have a vegetable, don't pick another?
                # Actually enforcing 1 V per day means we pick V exactly once.
                
                # Meat Type Uniqueness
                m_type = self.identify_meat_type(d.name)
                
                # Fish Limit
                if m_type == 'Fish' and weekly_fish_count >= 2:
                    continue
                    
                # Daily Meat Uniqueness
                if m_type and m_type in daily_meats:
                    continue
                    
                valid.append(d)
                
            if not valid:
                return []
                
            # Pick
            picked = []
            if len(valid) >= count:
                picked = random.sample(valid, count)
            else:
                picked = valid # Take what we can
                
            for p in picked:
                m = self.identify_meat_type(p.name)
                if m: daily_meats.add(m)
                
            return picked

        # 1. Vegetable (Strictly 1)
        v_picked = pick_valid('Vegetable', self.by_category['Vegetable'], 1)
        meal.extend(v_picked)
        
        # 2. Protein
        # If Combo -> No Protein
        if 'Combo' not in staple:
            p_picked = pick_valid('Protein', self.by_category['Protein'], 1)
            meal.extend(p_picked)
            
        # 3. Egg (if Egg Day)
        if is_egg_day:
            e_picked = pick_valid('Egg', self.by_category['Egg'], 1)
            meal.extend(e_picked)
            
        # 4. Other
        # Normal Staple + Egg Day -> Need 1 Other
        # Normal Staple + Non-Egg -> Need 2 Others
        if 'Combo' not in staple:
            needed_others = 1 if is_egg_day else 2
            o_picked = pick_valid('Other', self.by_category['Other'], needed_others)
            meal.extend(o_picked)
            
        # 5. Fill Remaining (Fallback)
        # Rules: 
        # - Max 1 Veg (Already picked 1) -> DO NOT pick Veg.
        # - No Meat Duplicates.
        # - No Fish if limit reached.
        # - No Protein if Combo (User: "配菜就不安排蛋白質". Strict?)
        #   If User implies "Main dish is combo, so no EXTRA protein side", then yes.
        #   So filling pool should be 'Other' or 'Egg' (if not egg day? but matched Egg rule).
        #   Actually, if we are short on dishes, we usually drag from Other?
        
        while len(meal) < target_sides:
            # Pool: Other? Can we pick extra Protein? 
            # If Normal Staple: We have 1P, 1V. If Non-Egg, 2O. (Total 4). Full.
            # If Egg Day (Normal): 1P, 1V, 1E. (Total 3). Target is 3?
            # Previous logic said "1P+1V+1E (+1 Random if n=4)". 
            # Wait, user constraints might imply strictly structured meals.
            # "每天只會安排一個vegetable類別" -> fixed 1 V.
            # "當主食為combo, 配菜不安排蛋白質" -> fixed 0 P.
            # "每天不重複肉類".
            
            # If we need to fill:
            # Can we duplicate categories? 
            # If we need 4th dish on Egg Day (Normal Staple)?
            # Maybe we should stick to:
            # Egg Day: P + V + E + (Other?)
            # Or is Egg Day just 3 dishes?
            # Let's assume we fill with 'Other' or 'Protein' (if allowed).
            
            pool_cats = ['Other']
            if 'Combo' not in staple:
                pool_cats.append('Protein') # Allowed second protein?
                # User: "每天出現的肉類不會重複" -> implies multiple meat dishes allowed IF types differ.
                
            candidates = []
            for cat in pool_cats:
                candidates.extend(self.by_category[cat])
                
            fillers = pick_valid('Fill', candidates, 1)
            if fillers:
                meal.append(fillers[0])
            else:
                break # Cannot fill
                
        return meal

    def generate_month_plan(self, days=28, start_date=None):
        import datetime
        
        if start_date is None:
            start_date = datetime.date.today()
            
        plan = []
        
        # State tracking
        current_week = None
        weekly_used_dishes = set()
        weekly_fish_count = 0
        last_combo_date = None
        
        # Holiday List for 2026 (Taiwan)
        # Assuming manual entry based on user request "Refer to Taiwan Holidays"
        # Source: Directorate-General of Personnel Administration (approximate)
        holidays_2026 = set()
        
        def add_range(start_str, end_str):
            s = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
            e = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
            curr = s
            while curr <= e:
                holidays_2026.add(curr)
                curr += datetime.timedelta(days=1)
                
        # Jan 1
        holidays_2026.add(datetime.date(2026, 1, 1))
        # LNY: Feb 14 - Feb 22
        add_range("2026-02-14", "2026-02-22")
        # Peace Day: Feb 27 - Mar 1
        add_range("2026-02-27", "2026-03-01")
        # Tomb Sweeping: Apr 3 - Apr 6
        add_range("2026-04-03", "2026-04-06")
        # Labor Day: May 1 - May 3
        add_range("2026-05-01", "2026-05-03")
        # Dragon Boat: Jun 19 - Jun 21
        add_range("2026-06-19", "2026-06-21")
        # Moon Festival: Sep 25 - Sep 28
        add_range("2026-09-25", "2026-09-28")
        # Double Ten: Oct 9 - Oct 11
        add_range("2026-10-09", "2026-10-11")
        # Retrocession: Oct 24 - Oct 26
        add_range("2026-10-24", "2026-10-26")
        # Constitution: Dec 25 - Dec 27
        add_range("2026-12-25", "2026-12-27")
        
        # Pre-calculate dates
        calendar_dates = []
        for i in range(days):
            d = start_date + datetime.timedelta(days=i)
            calendar_dates.append(d)
        
        # Group by ISO Week to manage resets
        # Logic: Iterating day by day. Check if week number changes.
        
        for current_date in calendar_dates:
            year, week, weekday = current_date.isocalendar() # Mon=1, Sun=7
            week_key = (year, week)
            
            # Reset counters on new week
            if week_key != current_week:
                weekly_used_dishes = set()
                weekly_fish_count = 0
                current_week = week_key
            
            day_data = {
                'Day': (current_date - start_date).days + 1,
                'Date': current_date,
                'DateStr': current_date.strftime("%Y-%m-%d"),
                'Weekday': current_date.strftime("%a"),
                'Staple': '',
                'Dinner_Objects': [],
                'Dinner': [],
                'Lunch_Objects': [] # Empty
            }
            
            # Skip weekends (Sat=6, Sun=7) OR Holidays
            is_holiday = (current_date in holidays_2026)
            if weekday > 5 or is_holiday:
                if is_holiday:
                    day_data['Staple'] = 'Holiday'
                plan.append(day_data)
                continue
                
            # Weekday Logic
            # Egg Days: Random 3 days of Mon(1)..Fri(5)
            # We need to know WHICH days are egg days for this specific week.
            # Deterministic/Consistent egg days? Or Random?
            # "Weekly Egg Rule: Exactly 3 weekdays".
            # We need to decide egg days for the WHOLE week when we enter the week.
            
            # Quick hack: Generate egg schedule on the fly if not exists
            if not hasattr(self, 'egg_schedule') or self.egg_schedule_week != week_key:
                self.egg_schedule_week = week_key
                # Pick 3 days from 1..5
                days_indices = sorted(random.sample(range(1, 6), 3))
                self.egg_days = set(days_indices)
                
            is_egg_day = (weekday in self.egg_days)
            
            # Staple
            # Need to get category first to determine counts
            # Staple
            # Need to get category first to determine counts
            staple_name = self.get_daily_staple(current_date, is_egg_day, last_combo_date)
            
            if 'Combo' in staple_name:
                last_combo_date = current_date

            # get_daily_staple returns actual name now? 
            # No, looking at my previous view, lines 69-110 in planner.py:
            # It returns `selected` which is a category string e.g. 'Rice', 'Combo (Rice)'.
            # Wait, viewing the file content again...
            # The view showed `get_daily_staple` returning `selected`.
            # `selected` comes from `allowed_types` which is `['Rice', ... 'Combo (Rice)']`.
            # So it returns CATEGORY.
            
            staple_cat = staple_name
            # Select specific dish name for staple
            # Assuming staples are not in `dishes` list but hardcoded or generic?
            # Previous summary said: "All staple categories now display a specific dish name ... in CSV".
            # DISHES CSV has: `咖哩飯,Combo (Rice),...`, `飯,Rice,`, `雞湯麵,Combo (Noodle)...`
            # So I need to pick a Dish object from `self.by_category[staple_cat]`.
            
            staple_dish_name = staple_cat # Default
            s_options = self.by_category[staple_cat]
            if s_options:
                s_dish = random.choice(s_options)
                staple_dish_name = s_dish.name
            
            day_data['Staple'] = staple_dish_name
            
            # Dinner
            dinner_dishes = self.generate_dinner(staple_cat, is_egg_day, weekly_used_dishes, weekly_fish_count)
            day_data['Dinner_Objects'] = dinner_dishes
            day_data['Dinner'] = [d.name for d in dinner_dishes]
            
            # Update trackers
            for d in dinner_dishes:
                weekly_used_dishes.add(d.name)
                if self.identify_meat_type(d.name) == 'Fish':
                    weekly_fish_count += 1
            
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
