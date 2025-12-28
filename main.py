import argparse
import sys
import os
from planner import load_dishes_from_csv, MealPlanner, save_plan_to_csv, save_shopping_list
from html_reporter import generate_html_report

def main():
    parser = argparse.ArgumentParser(description="Weekly Meal Planner & Shopping List Generator")
    parser.add_argument('--input', '-i', default='dishes.csv', help='Path to the input dishes CSV file')
    parser.add_argument('--days', '-d', type=int, default=28, help='Number of days to plan (default: 28)')
    parser.add_argument('--output-plan', '-o', default='meal_plan.csv', help='Output filename for the meal plan')
    parser.add_argument('--output-shop', '-s', default='shopping_list.csv', help='Output filename for the shopping list')
    parser.add_argument('--output-html', '-w', default='meal_plan_report.html', help='Output filename for the Web Report')
    parser.add_argument('--start-date', type=str, default=None, help='Start date in YYYY-MM-DD format (default: today)')
    
    args = parser.parse_args()
    
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        print("Please provide a valid CSV file with columns: Dish Name, Category, Ingredients")
        sys.exit(1)
        
    print(f"Loading dishes from {input_path}...")
    dishes = load_dishes_from_csv(input_path)
    
    if not dishes:
        print("Error: No dishes loadable from file. Check format.")
        sys.exit(1)
        
    print(f"Loaded {len(dishes)} dishes.")
    
    planner = MealPlanner(dishes)
    
    start_date = None
    if args.start_date:
        import datetime
        try:
            start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d").date()
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD.")
            sys.exit(1)
    
    print(f"Generating plan for {args.days} days starting from {start_date if start_date else 'Today'}...")
    plan = planner.generate_month_plan(days=args.days, start_date=start_date)
    
    save_plan_to_csv(plan, args.output_plan)
    
    print("Aggregating ingredients...")
    shopping = planner.aggregate_ingredients(plan)
    save_shopping_list(shopping, args.output_shop)
    
    print("Generating Web Report...")
    generate_html_report(plan, shopping, args.output_html)
    
    print("\nSuccess! Files generated:")
    print(f" - Web Report: {os.path.abspath(args.output_html)}")
    print(f" - Plan: {os.path.abspath(args.output_plan)}")
    print(f" - Shopping List: {os.path.abspath(args.output_shop)}")

if __name__ == "__main__":
    main()
