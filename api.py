from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import numpy as np
import os
import traceback

app = FastAPI()

# Simple middleware to ensure every error returns JSON (prevents front-end fetch .json() from rejecting)
@app.middleware("http")
async def catch_exceptions_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        tb = traceback.format_exc()
        print("Unhandled exception during request:\n", tb)
        return JSONResponse(status_code=500, content={"error": "internal_server_error", "detail": str(e)})

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data
monthly_sales = {}
ingredient_df = None
shipment_df = None

# Helper to coerce numpy/pandas types to native Python and handle NaN
def safe_val(v, default=0):
    try:
        if v is None:
            return default
        if isinstance(v, (np.generic,)):
            return v.item()
        if pd.isna(v):
            return default
        return v
    except Exception:
        return default

def load_data():
    global monthly_sales, ingredient_df, shipment_df
    
    monthly_sales = {}
    ingredient_df = None
    shipment_df = None

    # Load monthly sales files
    for month in ['May', 'June', 'July', 'August', 'September', 'October']:
        file = f"{month}.xlsx"
        if os.path.exists(file):
            try:
                monthly_sales[month] = pd.read_excel(file, engine="openpyxl")
                print(f"✓ Loaded {file}")
            except Exception as e:
                print(f"✗ Error loading {file}: {e}")

    # Load ingredient data
    if os.path.exists("MSY Data - Ingredient.csv"):
        try:
            ingredient_df = pd.read_csv("MSY Data - Ingredient.csv")
            print(f"✓ Loaded ingredient data")
        except Exception as e:
            ingredient_df = None
            print(f"✗ Error loading ingredient CSV: {e}")
    
    # Load shipment data
    if os.path.exists("MSY Data - Shipment.csv"):
        try:
            shipment_df = pd.read_csv("MSY Data - Shipment.csv")
            print(f"✓ Loaded shipment data")
        except Exception as e:
            shipment_df = None
            print(f"✗ Error loading shipment CSV: {e}")

@app.on_event("startup")
async def startup():
    load_data()
    print("\n=== Dashboard Ready ===")
    print("Open: http://127.0.0.1:8000\n")

@app.get("/")
def home():
    if os.path.exists("dashboard.html"):
        return FileResponse("dashboard.html")
    return {"error": "dashboard.html not found"}

@app.get("/api/metrics")
def metrics():
    items = len(ingredient_df) if ingredient_df is not None else 0
    ingredients = len(shipment_df) if shipment_df is not None else 0
    
    weekly = 0
    alerts = 0
    if shipment_df is not None:
        try:
            if 'frequency' in shipment_df.columns and 'Number of shipments' in shipment_df.columns:
                freq = shipment_df['frequency'].astype(str).str.lower()
                num = shipment_df['Number of shipments'].apply(safe_val).astype(float)
                weekly = int(num[freq == 'weekly'].sum())
            if 'Number of shipments' in shipment_df.columns:
                alerts = int((shipment_df['Number of shipments'].apply(safe_val) >= 5).sum())
        except Exception as e:
            print("Error computing metrics:", e)
            weekly = 0
            alerts = 0
    
    return {
        "totalItems": int(items),
        "totalIngredients": int(ingredients),
        "weeklyShipments": int(weekly),
        "alertCount": int(alerts)
    }

@app.get("/api/ingredient-usage")
def ingredient_usage():
    if shipment_df is None:
        return {"labels": [], "data": []}
    
    try:
        df = shipment_df.copy()
        def weekly_calc(row):
            qty = safe_val(row.get('Quantity per shipment', 0)) * safe_val(row.get('Number of shipments', 0))
            freq = str(safe_val(row.get('frequency', ''))).lower()
            if 'weekly' in freq:
                return qty
            elif 'biweekly' in freq:
                return qty / 2
            elif 'monthly' in freq:
                return qty / 4
            return qty
        
        df['weekly_usage'] = df.apply(lambda r: weekly_calc(r), axis=1)
        if df['weekly_usage'].isnull().all():
            return {"labels": [], "data": []}
        top6 = df.nlargest(6, 'weekly_usage')
        labels = [str(x) for x in top6.get('Ingredient', pd.Series([])).tolist()]
        data = [int(safe_val(x, 0)) for x in top6['weekly_usage'].tolist()]
        return {"labels": labels, "data": data}
    except Exception as e:
        print("Error in ingredient-usage:", traceback.format_exc())
        return {"labels": [], "data": []}

@app.get("/api/sales-trends")
def sales_trends():
    if not monthly_sales:
        return {"labels": [], "datasets": []}
    
    months = ['May', 'June', 'July', 'August', 'September', 'October']
    available = [m for m in months if m in monthly_sales]
    
    categories = {
        "Ramen Dishes": ["Ramen"],
        "Fried Rice": ["Fried Rice"],
        "Wings & Cutlets": ["Wing", "Cutlet"],
        "Rice Noodles": ["Rice Noodle"]
    }
    
    datasets = []
    for cat_name, keywords in categories.items():
        counts = []
        for month in available:
            df = monthly_sales[month]
            count = 0
            if 'Group' in df.columns:
                for keyword in keywords:
                    count += df['Group'].astype(str).str.contains(keyword, case=False, na=False).sum()
            counts.append(count)
        
        datasets.append({"label": cat_name, "data": counts})
    
    return {"labels": available, "datasets": datasets}

@app.get("/api/forecast")
def forecast():
    if not monthly_sales:
        return {"labels": [], "actual": [], "predicted": []}
    
    months = ['May', 'June', 'July', 'August', 'September', 'October']
    available = [m for m in months if m in monthly_sales]
    actual = [len(monthly_sales[m]) for m in available]
    
    if len(actual) >= 2:
        x = np.arange(len(actual))
        y = np.array(actual)
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        f1 = int(p(len(actual)))
        f2 = int(p(len(actual) + 1))
    else:
        f1 = int(actual[-1] * 1.05) if actual else 500
        f2 = int(f1 * 1.05)
    
    labels = available + ["Forecast 1", "Forecast 2"]
    actual_data = actual + [None, None]
    predicted_data = [None] * (len(actual) - 1) + [actual[-1] if actual else 500, f1, f2]
    
    return {"labels": labels, "actual": actual_data, "predicted": predicted_data}

@app.get("/api/alerts")
def alerts():
    result = []
    
    if shipment_df is not None:
        for _, row in shipment_df.iterrows():
            ingredient = str(row['Ingredient'])
            
            if row['Number of shipments'] >= 5:
                result.append({
                    "type": "warning",
                    "title": f"{ingredient} - High Frequency",
                    "message": f"{int(row['Number of shipments'])} shipments {row['frequency']}"
                })
            
            if 'egg' in ingredient.lower():
                total = int(row['Quantity per shipment'] * row['Number of shipments'])
                result.append({
                    "type": "critical",
                    "title": f"{ingredient} - Critical Item",
                    "message": f"Requires {total} {row['Unit of shipment']} per {row['frequency']}"
                })
    
    return result[:3]

@app.get("/api/shipment-schedule")
def shipment_schedule():
    if shipment_df is None:
        return []
    
    try:
        emojis = {'beef': '🥩', 'chicken': '🍗', 'ramen': '🍜', 'egg': '🥚', 
                  'rice': '🌾', 'onion': '🧅', 'carrot': '🥕', 'flour': '🌾'}
        
        schedule = []
        for _, row in shipment_df.iterrows():
            ingredient = str(safe_val(row.get('Ingredient', 'Unknown')))
            emoji = '📦'
            for key, icon in emojis.items():
                if key in ingredient.lower():
                    emoji = icon
                    break
            
            frequency = safe_val(row.get('frequency', 'unknown'))
            num_ship = int(safe_val(row.get('Number of shipments', 0)))
            schedule.append({
                "ingredient": f"{emoji} {ingredient}",
                "frequency": f"{frequency} ({num_ship}x)",
                "nextDelivery": f"{int(np.random.randint(1, 7))} days",
                "overdue": False
            })
        return schedule
    except Exception:
        print("Error in shipment_schedule:", traceback.format_exc())
        return []

@app.get("/api/cost-analysis")
def cost_analysis():
    if shipment_df is None:
        return []
    
    costs = {'beef': 8, 'chicken': 4, 'egg': 0.30, 'rice': 2,
             'ramen': 1.5, 'flour': 0.50, 'onion': 0.10, 'carrot': 3}
    
    analysis = []
    for _, row in shipment_df.iterrows():
        ingredient = str(row['Ingredient']).lower()
        
        cost_per_unit = 3
        for key, value in costs.items():
            if key in ingredient:
                cost_per_unit = value
                break
        
        qty = row['Quantity per shipment'] * row['Number of shipments']
        freq = str(row['frequency']).lower()
        
        if 'weekly' in freq:
            weekly_qty = qty
        elif 'biweekly' in freq:
            weekly_qty = qty / 2
        elif 'monthly' in freq:
            weekly_qty = qty / 4
        else:
            weekly_qty = qty
        
        weekly_cost = weekly_qty * cost_per_unit
        
        analysis.append({
            "ingredient": row['Ingredient'],
            "details": f"{int(weekly_qty)} {row['Unit of shipment']}/week @ ${cost_per_unit}/{row['Unit of shipment']}",
            "cost": f"${int(weekly_cost)}/wk",
            "percentage": min(100, int((weekly_cost / 1500) * 100))
        })
    
    analysis.sort(key=lambda x: int(x['cost'].replace('$', '').replace('/wk', '')), reverse=True)
    return analysis[:5]

@app.get("/api/recommendations")
def recommendations():
    recs = []
    
    if shipment_df is not None:
        high_freq = shipment_df[shipment_df['Number of shipments'] >= 4]
        if len(high_freq) > 0:
            items = ', '.join(high_freq['Ingredient'].head(2).tolist())
            recs.append({
                "type": "success",
                "title": "Bulk Buying Opportunity",
                "message": f"Consider monthly contracts for {items} to save 10-15%"
            })
        
        fresh = ['Green Onion', 'Cilantro', 'Bokchoy']
        if any(item in shipment_df['Ingredient'].values for item in fresh):
            recs.append({
                "type": "success",
                "title": "Reduce Waste",
                "message": "Fresh vegetables have high spoilage. Optimize for 5-day freshness."
            })
    
    if ingredient_df is not None:
        recs.append({
            "type": "success",
            "title": "Menu Engineering",
            "message": f"Promote dishes with overlapping ingredients ({len(ingredient_df)} items)."
        })
    
    return recs

@app.get("/api/protein-forecast")
def protein_forecast():
    if shipment_df is None:
        return {}
    
    proteins = {}
    for _, row in shipment_df.iterrows():
        ingredient = str(row['Ingredient']).lower()
        qty = row['Quantity per shipment'] * row['Number of shipments']
        freq = str(row['frequency']).lower()
        
        if 'weekly' not in freq:
            qty = qty / 2 if 'biweekly' in freq else qty / 4
        
        if 'beef' in ingredient:
            proteins['beef'] = {
                "amount": f"{int(qty)} {row['Unit of shipment']}",
                "shipments": f"{int(row['Number of shipments'])} shipments"
            }
        elif 'chicken' in ingredient and 'wing' not in ingredient:
            proteins['chicken'] = {
                "amount": f"{int(qty)} {row['Unit of shipment']}",
                "shipments": f"{int(row['Number of shipments'])} shipments"
            }
    
    if 'pork' not in proteins:
        proteins['pork'] = {"amount": "40 lbs", "shipments": "estimated"}
    
    return proteins

@app.get("/api/ingredient-matrix")
def ingredient_matrix():
    if ingredient_df is None:
        return []
    
    matrix = []
    for _, row in ingredient_df.iterrows():
        ingredients = []
        for col in ingredient_df.columns[1:]:
            val = row[col]
            if pd.notna(val) and val != 0 and val != '':
                clean = col.replace('(g)', '').replace('(count)', '').replace('(pcs)', '').strip()
                ingredients.append(clean)
        
        protein = "0"
        for col_name in ['braised beef used (g)', 'Braised Chicken(g)', 'Braised Pork(g)']:
            if col_name in row.index and pd.notna(row[col_name]) and row[col_name] > 0:
                protein = str(int(row[col_name]))
                break
        
        complexity = "Low" if len(ingredients) <= 3 else "Medium" if len(ingredients) <= 6 else "High"
        
        matrix.append({
            "menuItem": row['Item name'],
            "keyIngredients": ", ".join(ingredients[:4]),
            "protein": protein,
            "complexity": complexity
        })
    
    return matrix

if __name__ == "__main__":
    import uvicorn
    print("\n🍜 Starting Mai Shan Yun Dashboard...")
    uvicorn.run(app, host="127.0.0.1", port=8000)