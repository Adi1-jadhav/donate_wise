# 🧠 DonateWise – AI-Powered NGO Donation Tracker

[Live demo on Vercel](https://donatewise.vercel.app/)

DonateWise is a full-stack donation management system that seamlessly connects generous donors with verified NGOs. It features AI-powered auto-categorization of donations, smart pickup recommendations, dynamic live tracking, and beautiful HTML email notifications to ensure transparency and efficiency in charitable logistics.

--- 

## ✨ Features

- **🤖 AI Categorization & Impact Prediction** – Automatically classifies donations and estimates their impact (working, new, etc.) based on visual and textual heuristics.
- **🚚 Smart Pickup Logic** – Analyzes quantity, condition, and category to intelligently recommend whether an NGO should dispatch a vehicle.
- **📦 End-to-End Live Tracking** – Donors can track their donations through states: Pending, Claimed, Dispatched, and Fulfilled.
- **📧 Premium Email Notifications** – Beautiful, branded HTML emails sent automatically when donations are claimed, dispatched, or delivered.
- **🏅 Donor Impact Certificates & Badges** – Gamification features rewarding users based on their donation milestones.
- **🔐 NGO Verification Workflow** – Admin approval system for secure and trustworthy NGO onboarding.
- **📊 Real-time Dashboard** – Live activity feeds, visual data charts, and map statistics for donors and admins.

---

## 🛠️ Tech Stack

| Layer | Tools / Libraries |
| :--- | :--- |
| **Backend** | Python, Flask, REST APIs |
| **Database** | MongoDB Atlas (NoSQL Cloud Database) |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Storage** | Cloudinary (Secure Image Hosting) |
| **Email Service** | `smtplib` + Gmail SMTP with background threading |
| **Deployment** | Vercel (Serverless Functions) |

---

## 👥 User Roles

| Role | Capabilities |
| :--- | :--- |
| **Donor** | Submit donations (with images), track claim status, earn badges & certificates, view live feeds. |
| **NGO** | Register for approval, view active and nearby donations, claim items, update pickup statuses (Dispatched, Fulfilled). |
| **Admin** | Verify & approve pending NGOs, monitor platform statistics, oversee all donations and users. |

---

## 🚀 Setup & Installation (Local Development)

> **Prerequisites**
> - Python 3.10+
> - MongoDB Atlas Account (or Local MongoDB Server)
> - Cloudinary Account (for image uploads)
> - Gmail Account (for sending automated emails)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Adi1-jadhav/DonateWise.git
   cd DonateWise
   ```

2. **Set up a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory and add your credentials:
   ```env
   SECRET_KEY=your_super_secret_key_here

   # Database
   MONGO_URI=mongodb+srv://<user>:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
   MONGO_DB_NAME=donatewise

   # Cloudinary
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret

   # Email
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_app_password
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Initialize the Database (First-time setup only)**
   Open your browser and navigate to:
   ```
   http://localhost:5000/_init_db
   ```
   *This creates database indexes and the default Admin account (`admin@donatewise.com` / `admin123`).*

---

## 🌐 Deployment (Vercel)

DonateWise is configured for seamless deployment on Vercel using the provided `vercel.json` file. 

1. Push your code to a GitHub repository.
2. Import the repository into your Vercel Dashboard.
3. In the Vercel Project Settings, add all the Environment Variables listed in Step 4 above.
4. Deploy the project.
5. Visit `https://your-project.vercel.app/_init_db` to initialize your cloud database.
