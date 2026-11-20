# 👕 Clothing Store Management System

A clean, lightweight, and production-ready **Inventory & Point-of-Sale (POS) Management System** built with **Python**, **Streamlit**, and **SQLite**. Designed for retail clothing stores to manage stock, process sales with automatic inventory deduction, and track system audit logs.

![Python](https://shields.io)
![Streamlit](https://shields.io)
![SQLite](https://shields.io)
![License](https://shields.io)

---

## ✨ Features

* **🔐 Admin Authentication:** Secure login screen powered by **SHA-256** password hashing and constant-time comparison (`hmac.compare_digest`).
* **📦 Inventory Dashboard:** Real-time KPI metrics (Total SKUs, Total Units, Inventory Valuation, Low-Stock Alerts), instant search/filtering by name or color, and safe item deletion.
* **➕ Smart Stock Management:** Add new clothing items with size, color, price, and quantity—automatically merges stock if an identical item already exists.
* **💳 Point of Sale (POS):** Process customer checkouts with automatic stock validation, total price calculation, and instant SQLite inventory deduction.
* **📜 System Audit Logs:** Built-in activity logging (`store_system.log`) tracking logins, inventory additions, sales, and deletions directly in the UI.

---

## 📂 Project Structure

```text
clothing-store-management/
├── app.py              # Main Streamlit UI, navigation, and session management
├── database.py         # SQLite connection manager and CRUD/POS operations
├── security.py         # SHA-256 authentication & input validation logic
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com
cd clothing-store-management
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🔑 Default Admin Credentials

| Field | Value |
| :--- | :--- |
| **Default Password** | `admin123` |

> **Security Note:** Before deploying to a public environment, update `DEFAULT_ADMIN_HASH` in `security.py` or load your password hash via `st.secrets` / environment variables.

---

## 🛠️ Tech Stack

* **Frontend / UI:** [Streamlit](https://streamlit.io)
* **Database:** [SQLite3](https://sqlite.org) (Zero-configuration local relational database)
* **Data Processing:** [Pandas](https://pydata.org)
* **Security & Logging:** Python Standard Library (`hashlib`, `hmac`, `re`, `logging`)

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
