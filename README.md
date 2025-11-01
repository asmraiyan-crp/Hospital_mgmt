# Hospital Patient Allocation System

A Django-based system to automatically allocate patients to hospitals based on priority levels and available beds using **Maximum Flow Algorithm**. Designed for emergency response and disaster management.

---

## Features

- **Patient Management**
  - Add, update, and view patient information.
  - Set priority levels for patients: Critical, Top, Mid, Low.
  - Automatic hospital assignment based on priority.

- **Hospital Management**
  - Add, update, and view hospitals.
  - Track available beds for different priority levels.
  - Automatic bed allocation updates after patient assignment.

- **Automatic Allocation**
  - Uses **Max-Flow algorithm** to assign patients to hospitals efficiently.
  - Updates patient records and hospital bed counts automatically.
  - Supports multiple hospitals and dynamic patient inflow.

- **Emergency Response**
  - Can be extended to manage resources using **Knapsack algorithm**.
  - Prioritizes sending resources to high-need areas during disasters.

---

## Technology Stack

- **Backend:** Python 3.13, Django 5.2  
- **Database:** SQLite (default, can switch to MySQL/PostgreSQL)  
- **Algorithm:** Max-Flow for patient allocation, optional Knapsack for resource management  
- **Frontend:** Django Admin for management  

---

## Models

### Patient
- `name`: String
- `age`: Integer
- `address`: String
- `email`: String
- `emergency_contact`: String
- `priority_level`: Integer (1=Critical, 2=Top, 3=Mid, 4=Low)
- `hospital_name`: ForeignKey to Hospital (nullable)

### Hospital
- `name`: String
- `location`: String
- `critical_priority_avaiable_beds`: Integer
- `top_priority_avaiable_beds`: Integer
- `mid_priority_avaiable_beds`: Integer
- `low_priority_avaiable_beds`: Integer
- `total_beds`: Integer

---

## Installation

1. **Clone the repository**

```bash
git clone <repo_url>
cd hospital_mgmt
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Apply migrations**

```bash
python manage.py migrate
```

5. **Create superuser for admin**

```bash
python manage.py createsuperuser
```

6. **Run the development server**

```bash
python manage.py runserver
```

7. **Access the admin panel**

```
http://127.0.0.1:8000/admin/
```

---

## Usage

1. Add hospitals and set available beds in the admin panel.
2. Add patients with priority levels.
3. Use the **Run Allocation** action in the Patient admin page.
4. The system will:
   - Assign patients to hospitals using **Max-Flow**.
   - Update patient records with assigned hospital.
   - Update available bed counts in hospitals.

---

## Allocation Algorithm

- Uses a **Max-Flow graph**:
  - **Source Node (S):** Connects to all patients.
  - **Patient Nodes (P1, P2, …):** Connect to eligible hospitals based on priority.
  - **Hospital Nodes (H1, H2, …):** Connect to the sink with capacity equal to available beds.
  - **Sink Node (T):** Receives flow from hospitals.
- **Flow = Patient allocation**.  
- Can be extended to **resource allocation using Knapsack** for disaster scenarios.

---

## Directory Structure

```
hospital_mgmt/
├── allocation/       # Max-Flow logic & resource allocation utilities
├── core/             # Django apps: models, admin, views
├── hospital_mgmt/    # Django project settings
├── templates/        # Optional templates
├── manage.py
├── requirements.txt
└── README.md
```

---

## Notes

- This project is designed for **emergency/disaster scenarios** but can be adapted for normal hospital management.
- Ensure **priority levels** are correctly set for accurate allocation.
- Max-Flow algorithm can handle **hundreds of patients and multiple hospitals efficiently**.

---

## Future Enhancements

- Integrate **Knapsack algorithm** to optimize delivery of resources during disasters.
- Add **real-time dashboards** for hospital bed availability and patient flow.
- Support **multiple cities or regions** with distributed allocation.
- Implement **notification system** for patients and hospital staff.

---

## License

MIT License