import os
import webbrowser

def generate_html_report(plan, shopping_lists, output_file="meal_plan_report.html"):
    """
    Generates a premium-looking HTML report for the meal plan.
    """
    
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
        --other: #86efac;
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
        max-width: 1200px;
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
    
    /* Grid Layout for Weeks */
    .week-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 25px;
    }
    
    /* Shopping List Styles */
    .shop-week {
        background: var(--card-bg);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .shop-week h3 {
        color: var(--accent);
        margin-top: 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 10px;
    }
    .shop-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 10px;
        list-style: none;
        padding: 0;
    }
    .shop-item {
        background: rgba(255,255,255,0.03);
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        display: flex;
        justify-content: space-between;
    }
    .shop-count {
        color: var(--accent);
        font-weight: bold;
    }
    
    /* Meal Plan Table Styles */
    .day-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        transition: transform 0.2s;
    }
    .day-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .day-header {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 15px;
        color: var(--text-main);
    }
    
    .meal-block {
        margin-bottom: 15px;
    }
    .meal-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-muted);
        margin-bottom: 5px;
        font-weight: 700;
    }
    .dish-tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        background: rgba(255,255,255,0.1);
        margin: 2px;
        font-size: 0.9rem;
    }
    .dish-Protein { border-left: 3px solid var(--protein); }
    .dish-Egg { border-left: 3px solid var(--egg); }
    .dish-Other { border-left: 3px solid var(--other); }
    
    /* Animations */
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    
    .category-legend {
        text-align: center;
        margin-bottom: 20px;
        font-size: 0.9rem;
        color: var(--text-muted);
    }
    .legend-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
        margin-left: 15px;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        body { padding: 20px; }
        h1 { font-size: 2rem; }
    }
    """
    
    # HTML Builder
    html_content = [f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Meal Plan Dashboard</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Weekly Meal Planner</h1>
                <p class="subtitle">Delicious, Balanced, Effortless</p>
                
                <div class="category-legend">
                    <span class="legend-dot" style="background:var(--protein)"></span>Protein
                    <span class="legend-dot" style="background:var(--egg)"></span>Egg
                    <span class="legend-dot" style="background:var(--other)"></span>Other
                </div>
            </header>
            
            <div class="tabs">
                <button class="tab-btn active" onclick="openTab('plan')">Meal Schedule</button>
                <button class="tab-btn" onclick="openTab('shop')">Shopping List</button>
            </div>
            
            <div id="plan" class="tab-content active">
                <div class="week-grid">
    """]
    
    # Add Day Cards
    for day in plan:
        day_num = day['Day']
        html_content.append(f"""
            <div class="day-card">
                <div class="day-header">Day {day_num}</div>
                
                <div class="meal-block">
                    <div class="meal-title">Lunch</div>
                    {''.join([f'<div class="dish-tag dish-{d.category}">{d.name}</div>' for d in day['Lunch_Objects']])}
                </div>
                
                <div class="meal-block">
                    <div class="meal-title">Dinner</div>
                    {''.join([f'<div class="dish-tag dish-{d.category}">{d.name}</div>' for d in day['Dinner_Objects']])}
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
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
                
                // Show current
                document.getElementById(tabName).classList.add('active');
                
                // Active btn
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
        
        # Auto-open
        webbrowser.open(f'file://{os.path.abspath(output_file)}')
        
    except Exception as e:
        print(f"Error generating HTML: {e}")

