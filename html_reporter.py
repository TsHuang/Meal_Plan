import os
import webbrowser
import datetime

def generate_html_report(plan, shopping_lists, output_file="meal_plan_report.html"):
    """
    Generates a premium-looking HTML report for the meal plan.
    Uses a Calendar Layout (Sun-Sat).
    """
    
    # Pre-process plan into weeks for calendar grid
    # We need to pad the beginning if the first day isn't Sunday
    
    # 0 = Mon, 6 = Sun in Python's weekday()
    # But usually calendars are Sun=0, Mon=1...Sat=6 or Mon=0...Sun=6
    # User asked for Sun-Sat. 
    # Python msg: Mon=0, Sun=6.
    # We want visual grid: Sun | Mon | Tue ... | Sat
    
    calendar_days = []
    
    if plan:
        first_date = plan[0]['Date']
        # weekday(): Mon=0, Sun=6.
        # We want Sun to be index 0 in our grid.
        # Python: Mon(0) -> 1, Tue(1) -> 2 ... Sat(5)->6, Sun(6)->0
        start_dow = (first_date.weekday() + 1) % 7
        
        # Add empty padding days
        for _ in range(start_dow):
            calendar_days.append(None)
            
        # Add actual days
        for day in plan:
            calendar_days.append(day)
            
    # CSS Styles (Dark Mode, Premium Feel)
    css = """
    :root {
        --bg-color: #0f172a;
        --card-bg: #1e293b;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --accent: #38bdf8;
        --accent-glow: rgba(56, 189, 248, 0.3);
        --protein: #fca5a5;
        --egg: #fde047;
        --vegetable: #86efac;
        --other: #c084fc;
        --border: rgba(255,255,255,0.08);
    }
    body {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        background-color: var(--bg-color);
        color: var(--text-main);
        margin: 0;
        padding: 40px;
        line-height: 1.6;
    }
    .container {
        max-width: 1400px;
        margin: 0 auto;
    }
    header {
        text-align: center;
        margin-bottom: 40px;
        animation: fadeIn 1s ease-in;
    }
    h1 {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    p.subtitle {
        color: var(--text-muted);
        font-size: 1.2rem;
    }
    
    /* Tabs */
    .tabs {
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
        gap: 20px;
    }
    .tab-btn {
        background: transparent;
        border: 2px solid var(--card-bg);
        color: var(--text-muted);
        padding: 10px 30px;
        border-radius: 30px;
        cursor: pointer;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    .tab-btn.active, .tab-btn:hover {
        border-color: var(--accent);
        color: var(--accent);
        box-shadow: 0 0 15px var(--accent-glow);
    }
    
    .tab-content {
        display: none;
        animation: slideUp 0.5s ease;
    }
    .tab-content.active {
        display: block;
    }
    
    /* Calendar Grid */
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 15px;
    }
    
    .weekday-header {
        text-align: center;
        font-weight: bold;
        color: var(--accent);
        padding: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Day Card Styles */
    .day-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid var(--border);
        min-height: 200px;
        display: flex;
        flex-direction: column;
        position: relative;
    }
    /* Header & Rules */
    .rules-container {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 30px;
        font-size: 0.9rem;
        line-height: 1.5;
        color: var(--text-muted);
    }
    .rules-container h3 {
        color: var(--text-main);
        margin-top: 0;
        margin-bottom: 10px;
    }
    .rules-container ul {
        margin: 0;
        padding-left: 20px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
    }
    .rules-container li {
        margin-bottom: 4px;
    }

    .date-header {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 8px; /* Reduce bottom margin since badge is next */
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--border);
        padding-bottom: 8px;
    }
    .date-info {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .date-num {
        color: var(--text-main);
    }
    .date-weekday {
        font-size: 0.8rem;
        color: var(--text-muted);
        font-weight: normal;
    }
    .staple-row {
        margin-bottom: 12px;
        display: flex;
        align-items: center;
    }
    .staple-badge {
        background: rgba(56, 189, 248, 0.15);
        color: var(--accent);
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        border: 1px solid rgba(56, 189, 248, 0.3);
        display: inline-block;
        width: 100%; /* Make it span/fill for uniform look? Or just inline-block */
        text-align: center;
        box-sizing: border-box;
    }
    
    .meal-block {
        margin-bottom: 12px;
        flex-grow: 1;
    }
    .meal-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 4px;
        font-weight: 700;
        opacity: 0.8;
    }
    
    .dish-list {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .dish-tag {
        font-size: 0.85rem;
        padding: 4px 8px;
        background: rgba(255,255,255,0.05);
        border-radius: 4px;
        border-left-width: 3px;
        border-left-style: solid;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .dish-Protein { border-left-color: var(--protein); color: var(--protein); }
    .dish-Egg { border-left-color: var(--egg); color: var(--egg); }
    .dish-Vegetable { border-left-color: var(--vegetable); color: var(--vegetable); }
    .dish-Other { border-left-color: var(--other); color: var(--other); }
    
    /* Shopping List Styles */
    .shop-week {
        background: var(--card-bg);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid var(--border);
    }
    .shop-week h3 {
        color: var(--accent);
        margin-top: 0;
        border-bottom: 1px solid var(--border);
        padding-bottom: 10px;
    }
    .shop-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 15px;
        list-style: none;
        padding: 0;
    }
    .shop-item {
        background: rgba(255,255,255,0.03);
        padding: 10px 15px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .shop-count {
        color: var(--accent);
        font-weight: bold;
        background: rgba(56, 189, 248, 0.1);
        padding: 2px 8px;
        border-radius: 10px;
    }

    .category-legend {
        text-align: center;
        margin-bottom: 20px;
    }
    .legend-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
        margin-left: 15px;
    }

    /* Animations */
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    
    @media (max-width: 1024px) {
        .calendar-grid {
            grid-template-columns: repeat(1, 1fr); /* Stack on mobile */
        }
        .day-card {
            min-height: auto;
        }
    }
    """
    
    # HTML Builder
    html_content = [f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Monthly Meal Calendar</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Monthly Meal Calendar</h1>
                <p class="subtitle">Weekly Dinner Plan (Mon-Fri) & Shopping Assistant</p>
            </header>

            <div class="rules-container">
                <h3>🍱 Planning Rules</h3>
                <ul>
                    <li><strong>Schedule:</strong> Dinner Only (Mon-Fri). Weekends excluded.</li>
                    <li><strong>Egg Days (3/week):</strong> 1 Protein + 1 Veg + 1 Egg.</li>
                    <li><strong>Non-Egg Days (2/week):</strong> 1 Protein + 1 Veg + 2 Other (Requires Rice/Noodle).</li>
                    <li><strong>Staples:</strong> Rice/Noodle/Combo. Noodle max once every 14 days.</li>
                    <li><strong>Combo Meals:</strong> Served with 3 side dishes.</li>
                    <li><strong>Normal Meals:</strong> Served with 4 side dishes.</li>
                </ul>
            </div>
            
            <div class="tabs">
                <button class="tab-btn active" onclick="openTab('plan')">Calendar View</button>
                <button class="tab-btn" onclick="openTab('shop')">Shopping List</button>
            </div>
            
            <div id="plan" class="tab-content active">
                <div class="calendar-grid">
                    <div class="weekday-header">Sun</div>
                    <div class="weekday-header">Mon</div>
                    <div class="weekday-header">Tue</div>
                    <div class="weekday-header">Wed</div>
                    <div class="weekday-header">Thu</div>
                    <div class="weekday-header">Fri</div>
                    <div class="weekday-header">Sat</div>
    """]
    
    # Loop through grid cells
    for day in calendar_days:
        if day is None:
            # Empty / Padding Day (for start of month alignment)
            html_content.append('<div class="day-card empty"></div>')
        else:
            date_obj = day['Date']
            date_str = date_obj.strftime("%m/%d")
            is_weekend = len(day['Dinner_Objects']) == 0
            
            if is_weekend:
                 html_content.append(f"""
                <div class="day-card weekend">
                    <div class="date-header">
                        <span class="date-num">{date_str}</span>
                        <span class="date-weekday">{day['Weekday']}</span>
                    </div>
                    <div class="free-day-content">No Meal Plan</div>
                </div>
                """)
            else:
                staple_info = day.get('Staple', '')
                html_content.append(f"""
                <div class="day-card">
                    <div class="date-header">
                        <div class="date-info">
                            <span class="date-num">{date_str}</span>
                            <span class="date-weekday">{day['Weekday']}</span>
                        </div>
                    </div>
                    <div class="staple-row">
                        <div class="staple-badge">{staple_info}</div>
                    </div>
                    
                    <div class="meal-block">
                        <!-- <div class="meal-title">Dinner</div> -->
                        <div class="dish-list">
                        {''.join([f'<div class="dish-tag dish-{d.category}">{d.name}</div>' for d in day['Dinner_Objects']])}
                        </div>
                    </div>
                </div>
                """)
            
    html_content.append("""
                </div>
            </div>
            
            <div id="shop" class="tab-content">
    """)
    
    # Add Shopping List
    for week, counter in shopping_lists.items():
        html_content.append(f"""
            <div class="shop-week">
                <h3>Week {week}</h3>
                <ul class="shop-list">
        """)
        for ing, count in sorted(counter.items()):
            html_content.append(f'<li class="shop-item"><span>{ing}</span> <span class="shop-count">x{count}</span></li>')
        
        html_content.append("""
                </ul>
            </div>
        """)
        
    html_content.append("""
            </div>
        </div>
        
        <script>
            function openTab(tabName) {
                document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');
            }
        </script>
    </body>
    </html>
    """)
    
    full_html = "".join(html_content)
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"HTML Report generated: {output_file}")
        webbrowser.open(f'file://{os.path.abspath(output_file)}')
        
    except Exception as e:
        print(f"Error generating HTML: {e}")
