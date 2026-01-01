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
            is_holiday = day.get('Staple') == 'Holiday'
            
            if is_weekend or is_holiday:
                 card_class = "weekend" if is_weekend and not is_holiday else "holiday"
                 message = "No Meal Plan" if is_weekend and not is_holiday else "Holiday / No Meal"
                 html_content.append(f"""
                <div class="day-card {card_class}">
                    <div class="date-header">
                        <span class="date-num">{date_str}</span>
                        <span class="date-weekday">{day['Weekday']}</span>
                    </div>
                    <div class="{card_class}-content">{message}</div>
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

def generate_mobile_report(plan, shopping_list, output_file="meal_plan_mobile.html"):
    """
    Generates a mobile-optimized HTML report (Vertical List).
    """
    import datetime
    
    # CSS Styles (Mobile First)
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
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
        background-color: var(--bg-color);
        color: var(--text-main);
        margin: 0;
        padding: 20px;
        padding-top: env(safe-area-inset-top, 20px); /* Handle notch on iPhone */
        padding-bottom: env(safe-area-inset-bottom, 20px);
        line-height: 1.5;
        -webkit-text-size-adjust: 100%;
        -webkit-font-smoothing: antialiased; /* Crisp text on iOS */
    }
    .header {
        text-align: center;
        margin-bottom: 30px;
    }
    h1 {
        font-size: 2rem;
        margin-bottom: 5px;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        color: var(--text-muted);
        font-size: 1rem;
    }
    
    .day-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid var(--border);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .day-card.weekend {
        opacity: 0.5;
        padding: 15px;
        background: rgba(255,255,255,0.02);
    }
    
    .date-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 10px;
    }
    .date-left {
        display: flex;
        align-items: baseline;
        gap: 10px;
    }
    .date-num {
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-main);
    }
    .date-weekday {
        font-size: 1rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .staple-pill {
        background: rgba(56, 189, 248, 0.15);
        color: var(--accent);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    .dish-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .dish-item {
        background: rgba(255,255,255,0.03);
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #888;
        font-size: 1rem;
    }
    .dish-Protein { border-left-color: var(--protein); color: var(--protein); }
    .dish-Egg { border-left-color: var(--egg); color: var(--egg); }
    .dish-Vegetable { border-left-color: var(--vegetable); color: var(--vegetable); }
    .dish-Other { border-left-color: var(--other); color: var(--other); }
    
    .no-plan {
        text-align: center;
        color: var(--text-muted);
        font-style: italic;
    }
    
    .fab-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: var(--accent);
        color: #000;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.5);
        text-decoration: none;
        z-index: 100;
        font-size: 24px;
    }
    </style>
    """
    
    html_content = [f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
        
        <!-- iOS Support -->
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Meal Plan">
        
        <!-- Android Support -->
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="theme-color" content="#0f172a">
        
        <title>Meal Plan (Mobile)</title>
        <style>{css}</style>
    </head>
    <body>
        <div id="plan-view">
            <div class="header">
                <h1>📅 Meal Plan</h1>
                <p class="subtitle">Dinner Menu (Mon-Fri)</p>
            </div>
    """]
    
    # Generate Day Cards
    for day in plan:
        date_obj = day['Date']
        date_str = date_obj.strftime("%m/%d")
        
        is_weekend = len(day.get('Dinner_Objects', [])) == 0
        
        if is_weekend:
            html_content.append(f"""
            <div class="day-card weekend">
                <div class="date-row" style="margin-bottom:0; border-bottom: none;">
                    <div class="date-left">
                        <span class="date-num">{date_str}</span>
                        <span class="date-weekday">{day['Weekday']}</span>
                    </div>
                    <span style="font-size:0.9rem; opacity:0.7">Weekend</span>
                </div>
            </div>
            """)
        else:
            staple = day.get('Staple', 'Rice')
            html_content.append(f"""
            <div class="day-card">
                <div class="date-row">
                    <div class="date-left">
                        <span class="date-num">{date_str}</span>
                        <span class="date-weekday">{day['Weekday']}</span>
                    </div>
                    <div class="staple-pill">{staple}</div>
                </div>
                <div class="dish-list">
                    {''.join([f'<div class="dish-item dish-{d.category}">{d.name}</div>' for d in day['Dinner_Objects']])}
                </div>
            </div>
            """)
            
    html_content.append("""
        <div style="height: 60px;"></div> <!-- Spacer -->
    </div>
    </body>
    </html>
    """)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_content))
        print(f"Mobile Report generated: {output_file}")
    except Exception as e:
        print(f"Error generating Mobile HTML: {e}")

def generate_mobile_shopping_list(shopping_list, output_file="shopping_list_mobile.html"):
    """
    Generates a mobile-optimized Shopping List with checkboxes.
    """
    
    css = """
    :root {
        --bg-color: #0f172a;
        --card-bg: #1e293b;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --accent: #38bdf8;
        --border: rgba(255,255,255,0.08);
        --checked-bg: rgba(56, 189, 248, 0.1);
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: var(--bg-color);
        color: var(--text-main);
        margin: 0;
        padding: 20px;
        padding-top: env(safe-area-inset-top, 20px);
        padding-bottom: env(safe-area-inset-bottom, 20px);
        line-height: 1.5;
        -webkit-text-size-adjust: 100%;
    }
    .header {
        text-align: center;
        margin-bottom: 25px;
    }
    h1 {
        font-size: 1.8rem;
        margin-bottom: 5px;
        color: var(--accent);
    }
    
    .week-group {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 25px;
        border: 1px solid var(--border);
    }
    .week-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: var(--text-main);
        margin-top: 0;
        margin-bottom: 15px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .shop-items {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .shop-item {
        display: flex;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.03);
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .shop-item:last-child {
        border-bottom: none;
    }
    
    /* Custom Checkbox */
    .checkbox-custom {
        width: 24px;
        height: 24px;
        border: 2px solid var(--accent);
        border-radius: 6px;
        margin-right: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .checkbox-custom::after {
        content: "✔";
        color: var(--bg-color);
        font-size: 14px;
        font-weight: bold;
        opacity: 0;
        transform: scale(0.5);
        transition: all 0.2s;
    }
    
    .shop-item.checked {
        opacity: 0.4;
        text-decoration: line-through;
    }
    .shop-item.checked .checkbox-custom {
        background: var(--accent);
    }
    .shop-item.checked .checkbox-custom::after {
        opacity: 1;
        transform: scale(1);
    }
    
    .item-name {
        flex-grow: 1;
        font-size: 1.05rem;
    }
    .item-count {
        background: rgba(255,255,255,0.1);
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    </style>
    """
    
    html_content = [f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
        
        <!-- Mobile Meta -->
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="theme-color" content="#0f172a">
        
        <title>Shopping List</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="header">
            <h1>🛒 Shopping List</h1>
            <p style="color:#94a3b8; margin:0;">Tap to check off items</p>
        </div>
    """]
    
    for week, counter in shopping_list.items():
        html_content.append(f"""
        <div class="week-group">
            <h3 class="week-title">Week {week}</h3>
            <ul class="shop-items">
        """)
        
        for ing, count in sorted(counter.items()):
            html_content.append(f"""
                <li class="shop-item" onclick="this.classList.toggle('checked')">
                    <div class="checkbox-custom"></div>
                    <span class="item-name">{ing}</span>
                    <span class="item-count">x{count}</span>
                </li>
            """)
            
        html_content.append("</ul></div>")
        
    html_content.append("""
    </body>
    </html>
    """)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_content))
        print(f"Mobile Shopping List generated: {output_file}")
    except Exception as e:
        print(f"Error generating Shopping List HTML: {e}")

def generate_print_html(plan, output_file="meal_plan_a4.html"):
    """
    Generates a single-page A4 Landscape HTML optimized for Print-to-PDF.
    Mon-Fri Only. Uses Gap property for perfect borders.
    """
    
    # CSS for A4 Landscape
    css = """
    @page { 
        size: A4 landscape;
        margin: 5mm;
    }
    * {
        box-sizing: border-box;
    }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #000;
        background: #fff;
        margin: 0;
        padding: 0;
        font-size: 11px; /* Increased from 10px */
    }
    h1 {
        text-align: center;
        margin: 5px 0 5px 0;
        font-size: 18px; /* Larger header */
    }
    
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        grid-template-rows: 28px repeat(5, 1fr); /* Header slightly taller */
        width: 100%;
        height: 188mm; /* Maximized height for A4 Landscape (210mm - margins) */
        background-color: #000;
        gap: 1px;
        border: 1px solid #000;
    }
    
    /* Cells */
    .header-cell, .day-cell {
        background-color: #fff;
    }
    
    .header-cell {
        background: #f0f0f0;
        font-weight: bold;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
    }
    
    .day-cell {
        padding: 4px; /* Slightly more relaxing */
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .date-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 3px;
        font-weight: bold;
        font-size: 13px; /* Larger Date */
        border-bottom: 1px solid #eee;
        padding-bottom: 2px;
    }
    
    .staple {
        font-weight: bold;
        color: #000;
        background: #e0f2fe;
        padding: 2px 4px;
        border-radius: 4px;
        font-size: 11px; /* Larger Staple */
        margin-bottom: 3px;
        text-align: center;
        display: block;
    }
    
    .dish-list {
        display: flex;
        flex-direction: column;
        gap: 2px; /* Standard gap */
        justify-content: space-evenly; /* Spread out */
        flex-grow: 1;
    }
    .dish {
        padding: 1px 4px;
        border-radius: 2px;
        border: 1px solid #ddd;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 11px; /* Larger Dish Font */
        line-height: 1.3;
        font-weight: 500;
    }
    .dish-Protein { background: #fee2e2; }
    .dish-Egg { background: #fef3c7; }
    .dish-Vegetable { background: #dcfce7; }
    .dish-Other { background: #f3e8ff; }
    
    /* Print tweaks */
    @media print {
        body { -webkit-print-color-adjust: exact; }
    }
    """
    
    html_content = [f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Meal Plan (A4)</title>
        <style>{css}</style>
    </head>
    <body>
        <h1>📅 Monthly Meal Plan (Mon-Fri)</h1>
        
        <div class="calendar-grid">
            <div class="header-cell">Mon</div>
            <div class="header-cell">Tue</div>
            <div class="header-cell">Wed</div>
            <div class="header-cell">Thu</div>
            <div class="header-cell">Fri</div>
    """]

    calendar_days = []
    
    # Filter Mon-Fri
    workdays = [d for d in plan if d['Date'].weekday() < 5]

    if workdays:
        first_day = workdays[0]
        wd = first_day['Date'].weekday() # Mon=0
        
        # Padding for first week
        for _ in range(wd):
            calendar_days.append(None)
            
        for day in workdays:
            calendar_days.append(day)
            
    # Need to fill up to exactly 25 cells (5 weeks * 5 days) to ensure grid looks complete?
    # Or just let it flow. The CSS grid-template-rows: repeat(5, 1fr) expects 5 rows.
    # If we have fewer items, we should pad it to maintain structure.
    total_slots = 5 * 5 # 25 slots
    while len(calendar_days) < total_slots:
        calendar_days.append(None)
            
    # Fill grid
    for day in calendar_days:
        if day is None:
            html_content.append('<div class="day-cell" style="background:#fafafa;"></div>')
        else:
            date_str = day['Date'].strftime("%m/%d")
            
            cell_html = '<div class="day-cell">'
            cell_html += f'<div class="date-row"><span>{date_str}</span></div>'
            
            staple = day.get('Staple', '')
            if staple == 'Holiday':
                cell_html += f'<div class="staple" style="background: #fee2e2; color: #b91c1c;">HOLIDAY</div>'
                cell_html += '<div class="dish-list" style="align-items: center; justify-content: center; color: #ccc;">No Meal</div>'
            else:
                cell_html += f'<div class="staple">{staple}</div>'
                cell_html += '<div class="dish-list">'
                for d in day['Dinner_Objects']:
                    cell_html += f'<div class="dish dish-{d.category}">{d.name}</div>'
                cell_html += '</div>'
                
            cell_html += '</div>'
            html_content.append(cell_html)
            
    html_content.append("""
        </div>
    </body>
    </html>
    """)
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_content))
        print(f"Print Report generated: {output_file}")
    except Exception as e:
        print(f"Error generating Print HTML: {e}")
