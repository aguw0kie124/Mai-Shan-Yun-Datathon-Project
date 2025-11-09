# Mai-Shan-Yun-Datathon-Project
Mai Shan Yun Inventory Intelligence Dashboard
Overview

The Mai Shan Yun Inventory Intelligence Dashboard is a web application that turns raw restaurant data into actionable insights for inventory optimization. It's intended to help managers track ingredient usage, monitor shipments, identify cost drivers, and forecast future demand to minimize waste and prevent shortages.

Purpose and Key Insights

Purpose:
To provide restaurant managers with a single, interactive view of inventory operations — connecting ingredient data, shipments, and menu sales for smarter decision-making.

Key Insights:
  - Identify high-demand or low-stock ingredients before shortages occur.
  - Correlate menu item sales with ingredient consumption.
  - Track purchasing and shipment frequency to reduce overstocking.
  - Highlight top-cost ingredients to target for bulk buying.
  - Forecast ingredient demand based on sales trends.

Datasets Used:
  - Sales Data (.xlsx): Monthly menu item sales (May–October).
  - Ingredient Data (.csv): Ingredient names, categories, and usage quantities.
  - Shipment Data (.csv): Supplier information, frequency, and delivery schedules.
  - Purchase Logs (.csv): Historical purchase quantities and prices.

Integration Process:
  - Cleaned and merged with pandas in api.py.
  - Aggregated metrics (usage, cost, frequency) generated through FastAPI endpoints.
  - Frontend retrieves and visualizes data dynamically via JSON responses.

