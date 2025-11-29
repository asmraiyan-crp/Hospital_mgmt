# 🚚 BD LogisticsFlow -- Supply Chain Optimization System

BD LogisticsFlow is a full-stack logistics optimization system designed
to enhance transport planning and medical supply distribution across
districts in Bangladesh.\
It combines graph algorithms, dynamic programming, and a modern React
dashboard to deliver actionable insights for resource allocation.

## ✨ Features

### 🔵 Max-Flow Analysis

-   Computes the maximum transport capacity between districts.
-   Implemented using Edmonds--Karp (BFS-based Max-Flow algorithm).

### 🔵 Resource Optimization

-   Uses a 0/1 Knapsack Dynamic Programming algorithm.
-   Finds the most valuable combination of medical supplies that fit
    within the transport capacity.

### 🔵 Interactive Network Graph

-   Visualizes:
    -   District nodes\
    -   Transport routes\
    -   Link capacities\
    -   Active flow usage

### 🔵 Data Management

-   CSV Bulk Upload for:
    -   Transport Network (routes)
    -   Medical Resources
-   Full CRUD operations for routes and resources.

### 🔵 Modern Web UI

-   React (Vite)
-   Tailwind CSS
-   Lucide React Icons

## 🛠️ Tech Stack

### Backend

-   Django
-   Django REST Framework (DRF)
-   Python 3.x
-   SQLite
-   Max-Flow (Edmonds-Karp), 0/1 Knapsack (DP)

### Frontend

-   React (Vite)
-   Tailwind CSS
-   Lucide React
-   Fetch API

## ⚙️ Installation & Setup

### Prerequisites

-   Python 3.8+
-   Node.js & npm

## 1. Backend Setup (Django)

    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install django djangorestframework django-cors-headers
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

API runs at: http://localhost:8000

## 2. Frontend Setup (React)

    cd logistics_mgnt
    npm install
    npm run dev

Frontend runs at: http://localhost:5173

## 📖 Usage Guide

### 1. Initialize Transport Network

CSV Format:

    Source,Destination,Capacity
    Dhaka,Comilla,500

### 2. Add Medical Resources

CSV Format:

    Name,Volume,Priority,Quantity
    Oxygen Tank,40,10,50

### 3. Run Optimization

-   Computes Max Flow
-   Generates routing plan
-   Knapsack decides optimal resources

### 4. Visualize Network

Interactive flow graph.

## 📂 Project Structure

    root/
    ├── backend/
    │   ├── core/
    │   ├── logistics_project/
    │   └── manage.py
    ├── logistics_mgnt/
    │   ├── src/
    │   ├── tailwind.config.js
    │   └── vite.config.js
    └── README.md

## 🤝 Contributing

1.  Fork the repo\
2.  Create a feature branch\
3.  Commit and push\
4.  Open PR

## 📜 License

MIT License
