# 🧠 DonateWise – AI‑Powered NGO Donation Tracker

[Live demo on Render](https://helping-hand-intelligent-system-mvtv.onrender.com)

DonateWise is a full‑stack donation‑management system that connects donors with verified NGOs.  
It uses a lightweight Naïve‑Bayes model to auto‑categorize donations, recommends pickups, and ensures transparency in charitable logistics.

---

## ✨ Features

- **🔐 NGO Verification Workflow** – Admin approval system for secure donation claims.  
- **📦 Donation Categorization** – ML model predicts donation type (food, clothes, books, etc.).  
- **🚚 Pickup Recommendation** – Smart logic suggests pickups based on quantity, urgency, and category.  
- **🧾 Claim Management** – NGOs can claim donations with scheduled pickup times.  
- **📊 Admin Dashboard** – View, approve, and manage all donations.  
- **📱 Mobile‑Friendly UI** – Fully responsive design for donors and NGOs.

---

## 🛠️ Tech Stack

| Layer      | Tools / Libraries |
|------------|-------------------|
| **Backend**| Flask, MySQL, REST APIs |
| **Frontend**| HTML, CSS, Bootstrap |
| **ML Model**| Naïve Bayes (scikit‑learn) |
| **Email**  | `smtplib` + Gmail SMTP (SSL) |
| **Background jobs**| Python `threading` (email sending) |
| **Deployment**| Render (Flask app) + Railway (MySQL) |
| **Database**| MySQL (cloud‑hosted) |

---

## 👥 User Roles

| Role   | Capabilities |
|--------|--------------|
| **Donor** | Submit donations, request optional pickup. |
| **NGO**   | View approved donations, claim them, see pickup schedule. |
| **Admin** | Verify NGOs, approve/deny claims, monitor system activity. |

---

## 🤖 AI Integration

- **Donation Category Predictor** – Naïve Bayes classifier trained on donation titles & descriptions.  
- **Pickup Recommender** – Rule‑based engine that suggests a pickup when quantity > 5 or the predicted category is “perishable”.

---

## 🚀 Setup & Installation

> **Prerequisites**  
> - Python 3.10+  
> - Git  
> - MySQL server (local for development, Railway/Aiven for production)  

1. **Clone the repository**  

   ```bash
   git clone https://github.com/Adi1-jadhav/DonateWise.git
   cd DonateWise
