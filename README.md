# 🚚 Last Mile Delivery Tracker

An end-to-end **Last Mile Delivery Management System** built using **React (Vite)**, **FastAPI**, and **PostgreSQL**. The platform allows customers to create delivery orders, admins to manage zones and assign delivery agents, and agents to update delivery status in real time.

Designed as a logistics workflow application with authentication, pricing engine, delivery tracking, rescheduling, and admin analytics.

---

## 📌 Features

### 👤 Customer

* Register and Login securely using JWT authentication.
* Create delivery orders (B2B / B2C).
* Automatic shipping charge calculation.
* Track live order status.
* View delivery history.
* Request rescheduling if delivery fails.

### 🛠️ Admin

* Dashboard with delivery statistics.
* Create and manage delivery zones.
* Manage customers and delivery agents.
* Automatic agent assignment based on delivery zone.
* View all orders and delivery history.

### 🚴 Delivery Agent

* View assigned deliveries.
* Update delivery status.
* Mark deliveries as:

  * Picked Up
  * In Transit
  * Out For Delivery
  * Delivered
  * Failed Delivery
* Add failure reason and notes.

---

## 🏗️ Tech Stack

| Layer            | Technology                                |
| ---------------- | ----------------------------------------- |
| Frontend         | React.js + Vite                           |
| Styling          | CSS                                       |
| Backend          | FastAPI                                   |
| Authentication   | JWT Tokens                                |
| Database         | PostgreSQL (SQLite for local development) |
| ORM              | SQLAlchemy                                |
| Password Hashing | Passlib (bcrypt)                          |
| API Testing      | Swagger UI                                |
| Deployment       | Vercel (Frontend + Backend Services)      |

---

## 📂 Project Structure

```text
Last_Mile_Delivery/
│
├── frontend/                 # React + Vite application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── backend/                  # FastAPI backend
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── database.py
│   ├── main.py
│   ├── seed.py
│   └── requirements.txt
│
├── vercel.json               # Vercel multi-service configuration
├── README.md
└── .gitignore
```

---

## 🔄 Application Workflow

```text
Customer
    │
    ▼
Create Order
    │
    ▼
Shipping Charge Calculation
    │
    ▼
Admin Dashboard
    │
Assign Delivery Agent
    │
    ▼
Delivery Agent
    │
Update Status
    │
    ▼
Customer Tracking Page
    │
    ▼
Delivered / Failed / Rescheduled
```

---

## 📦 Delivery Status Flow

| Status           | Description                                  |
| ---------------- | -------------------------------------------- |
| Pending          | Order created successfully.                  |
| Assigned         | Delivery agent assigned.                     |
| Picked Up        | Parcel collected by agent.                   |
| In Transit       | Parcel is on the way.                        |
| Out For Delivery | Parcel is arriving today.                    |
| Delivered        | Delivery completed successfully.             |
| Failed Delivery  | Delivery attempt failed.                     |
| Rescheduled      | Customer requested another delivery attempt. |

---

## 💰 Shipping Charge Calculation

Shipping cost is calculated using:

* **Zone Type**

  * Intra Zone
  * Inter Zone

* **Customer Type**

  * B2B
  * B2C

* **Weight**

  * Actual Weight
  * Volumetric Weight

### Formula

```text
Volumetric Weight = (Length × Breadth × Height) / 5000

Billable Weight = Max(Actual Weight, Volumetric Weight)

Final Cost =
Base Rate × Billable Weight
+ COD Charges (if applicable)
```

---

## 🔐 Authentication

JWT-based authentication is implemented.

### Roles

| Role     | Access                  |
| -------- | ----------------------- |
| CUSTOMER | Create & Track Orders   |
| ADMIN    | Full Management Access  |
| AGENT    | Delivery Status Updates |

Authorization is verified on protected API routes.

---

## 🗄️ Database Tables

* Users
* Customers
* Delivery Agents
* Orders
* Tracking History
* Delivery Zones
* Rate Cards

Relationships are managed using SQLAlchemy ORM.

---

## 🚀 Local Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/iamshubhdeep/Last_Mile_Delivery.git

cd Last_Mile_Delivery
```

### 2️⃣ Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

Create `.env`

```env
DATABASE_URL=sqlite:///./lastmile.db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Seed database

```bash
python seed.py
```

Run server

```bash
python main.py
```

Backend URL

```text
http://localhost:8000
```

Swagger API

```text
http://localhost:8000/docs
```

### 3️⃣ Frontend Setup

```bash
cd frontend

npm install
```

Create `.env`

```env
VITE_API_URL=http://localhost:8000/api
```

Run frontend

```bash
npm run dev
```

Frontend URL

```text
http://localhost:5173
```

---

## ☁️ Deployment on Vercel

### Frontend

* Framework: **Vite**
* Root Directory: `frontend`

### Backend

* Runtime: **FastAPI (Python)**
* Root Directory: `backend`

### vercel.json

Routes `/api/*` to FastAPI and all other routes to React.

---

## 📮 Important API Endpoints

### Authentication

| Method | Endpoint             |
| ------ | -------------------- |
| POST   | `/api/auth/register` |
| POST   | `/api/auth/login`    |

### Orders

| Method | Endpoint                 |
| ------ | ------------------------ |
| POST   | `/api/orders/create`     |
| GET    | `/api/orders/my-orders`  |
| GET    | `/api/orders/{order_id}` |

### Tracking

| Method | Endpoint                      |
| ------ | ----------------------------- |
| GET    | `/api/tracking/{tracking_id}` |

### Admin

| Method | Endpoint                  |
| ------ | ------------------------- |
| GET    | `/api/admin/dashboard`    |
| POST   | `/api/admin/assign-agent` |
| POST   | `/api/admin/create-zone`  |

### Agent

| Method | Endpoint                              |
| ------ | ------------------------------------- |
| GET    | `/api/agent/orders`                   |
| PUT    | `/api/agent/update-status/{order_id}` |

---


## 🎯 Future Improvements

* Live GPS tracking.
* Google Maps integration.
* OTP verification during delivery.
* Email & SMS notifications.
* Delivery analytics dashboard.
* AI-based nearest agent assignment.
* Push notifications.

---

## 👨‍💻 Author

**Shubhdeep Singh**

B.Tech Computer Science Engineering
VIT Bhopal University

GitHub: https://github.com/iamshubhdeep
