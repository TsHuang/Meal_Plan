Meal Planner App - Walkthrough
I have successfully created your Weekly Meal Planner Application. This tool helps you automatically generate a balanced lunch and dinner schedule based on your own recipes and creates a shopping list for you.

Features
Automatic Planning: Generates a 4-week (or custom duration) plan.
Balanced Meals: Ensures a mix of Protein, Egg, and Other dishes daily.
Shopping List: Aggregates ingredients into a weekly shopping list.
Web Dashboard: Interactive HTML report to view your plan comfortably.
CSV Output: Outputs easy-to-read CSV files.
How to Use
1. Prepare Your Dishes
The app comes with a sample 

dishes.csv
. You can edit this file to add your own recipes. Format:

Dish Name,Category,Ingredients
Kung Pao Chicken,Protein,"Chicken, Peanuts, Chili"
Steamed Egg,Egg,Eggs
Stir-fried Cabbage,Other,Cabbage
Categories supported: Protein, Egg, Other

2. Run the Planner
Open a terminal in the folder C:\Users\USER\.gemini\antigravity\playground\shimmering-cosmic and run:

Default (28 Days):

python main.py
Custom Settings (e.g., 7 days, custom output names):

python main.py --days 7 --output-plan my_plan.csv --output-shop my_shopping.csv
3. Check the Output
The app will automatically open the Web Report in your browser. You will also find files in the folder:

meal_plan_report.html: The interactive dashboard.
meal_plan.csv: Your schedule (Day, Meal, Dish 1...Dish 4).
shopping_list.csv: Your weekly ingredient needs.
Files Created
planner.py: The core logic engine.
main.py: The command-line interface.
dishes.csv: The database of your recipes.
meal_plan.csv & shopping_list.csv: Generated outputs.
