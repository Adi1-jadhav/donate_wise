from db.database import get_db_connection
from werkzeug.security import generate_password_hash

def run_migrations():
    print("🚀 Starting database migrations...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Users Table
        print("Creating 'users' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255),
                role VARCHAR(20) DEFAULT 'donor'
            )
        """)

        # 2. NGOs info table
        print("Creating 'ngos' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ngos (
                id INT PRIMARY KEY,
                org_name VARCHAR(200),
                address TEXT,
                license_no VARCHAR(50),
                status VARCHAR(20) DEFAULT 'pending',
                FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 3. Donations Table
        print("Creating 'donations' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                title VARCHAR(200),
                description TEXT,
                predicted_category VARCHAR(50),
                quantity VARCHAR(50),
                pickup_status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                location VARCHAR(255),
                image_filename VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 4. Donation Claims Table
        print("Creating 'donation_claims' table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS donation_claims (
                id INT AUTO_INCREMENT PRIMARY KEY,
                donation_id INT,
                ngo_id INT,
                pickup_time DATETIME,
                status VARCHAR(20) DEFAULT 'claimed',
                FOREIGN KEY (donation_id) REFERENCES donations(id) ON DELETE CASCADE,
                FOREIGN KEY (ngo_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 5. NGO Needs Table
        print("Creating 'ngo_needs' table...")
        # Note: references 'ngos(id)' which is why 'ngos' table must exist first
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ngo_needs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ngo_id INT NOT NULL,
                category VARCHAR(50) NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                quantity INT NOT NULL DEFAULT 1,
                description TEXT,
                priority ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
                status ENUM('Open', 'Fulfilled') DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ngo_id) REFERENCES ngos(id) ON DELETE CASCADE
            )
        """)

        # 6. Ensure default Admin exists
        print("Checking for default admin...")
        hashed = generate_password_hash('admin123')
        cur.execute('INSERT IGNORE INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)', 
                   ("Admin", "admin@donatewise.com", hashed, "admin"))

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database migrations completed successfully.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_migrations()
