# Mai-Shan-Yun-Datathon-Project
Mai Shan Yun Inventory Intelligence Dashboard

## Overview
The Mai Shan Yun Inventory Intelligence Dashboard is a web application that turns raw restaurant data into actionable insights for inventory optimization. It's intended to help managers track ingredient usage, monitor shipments, identify cost drivers, and forecast future demand to minimize waste and prevent shortages.

## Purpose and Key Insights
**Purpose:**
To provide restaurant managers with a single, interactive view of inventory operations by connecting ingredient data, shipments, and menu sales for smarter decision-making.

**Key Insights:**
  - Identify high-demand or low-stock ingredients before shortages occur.
  - Correlate menu item sales with ingredient consumption.
  - Track purchasing and shipment frequency to reduce overstocking.
  - Highlight top-cost ingredients to target for bulk buying.
  - Forecast ingredient demand based on sales trends.

## Datasets Used
  - **Sales Data (.xlsx)**: Monthly menu item sales (May–October).
  - **Ingredient Data (.csv)**: Ingredient names, categories, and usage quantities.
  - **Shipment Data (.csv)**: Supplier information, frequency, and delivery schedules.
  - **Purchase Logs (.csv)**: Historical purchase quantities and prices.

**Integration Process:**
  - Cleaned and merged with pandas in `api.py`.
  - Aggregated metrics (usage, cost, frequency) generated through FastAPI endpoints.
  - Frontend retrieves and visualizes data dynamically via JSON responses.

## Features
- **Live Metrics Dashboard**: Real-time KPIs for menu items, ingredients, shipments, and alerts
- **Interactive Visualizations**: Chart.js-powered graphs for sales trends, ingredient usage, and demand forecasting
- **Cost Analysis**: Weekly breakdown of ingredient costs with percentage indicators
- **Smart Recommendations**: AI-based suggestions for bulk buying and waste reduction
- **Shipment Scheduling**: Track delivery frequencies and timing across all suppliers
- **Ingredient Matrix**: Analyze menu complexity and ingredient overlap for optimization

## Setup & Run Instructions

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Mai-Shan-Yun-Datathon-Project.git
cd Mai-Shan-Yun-Datathon-Project
```

2. **Install dependencies**
```bash
pip install fastapi uvicorn pandas numpy openpyxl
```

3. **Ensure data files are in the project root**
   - `May.xlsx`, `June.xlsx`, `July.xlsx`, `August.xlsx`, `September.xlsx`, `October.xlsx`
   - `MSY Data - Ingredient.csv`
   - `MSY Data - Shipment.csv`

### Running the Application

1. **Start the backend server**
```bash
python api.py
```
   The API will start at `http://127.0.0.1:8000`

2. **Access the dashboard**
   - Open your browser and navigate to: `http://127.0.0.1:8000`
   - The dashboard will automatically load and fetch data from the API

3. **Verify everything is working**
   - Check the terminal for successful data loading messages (✓)
   - The dashboard should display metrics, charts, and tables populated with data

### Troubleshooting
- **CORS errors**: Ensure the frontend is accessing `http://127.0.0.1:8000` (not localhost)
- **Missing data**: Verify all .xlsx and .csv files are in the correct directory
- **Module errors**: Run `pip install -r requirements.txt` if dependencies are missing


