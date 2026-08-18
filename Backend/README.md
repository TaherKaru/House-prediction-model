# Havenly backend

This Flask API stores accounts in MySQL. On startup it automatically creates
the configured database and the `users` table if they do not already exist.

## Configure MySQL

1. Start your MySQL service (for example, from XAMPP).
2. Copy `.env.example` to a new file called `.env` inside this `Backend` folder.
3. Set the credentials that work in your MySQL installation:

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=havenly
```

`MYSQL_DATABASE` may be changed to any new database name. The app creates it
and creates this table automatically:

```sql
users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Run

```powershell
cd Backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:5000/`. It reports `database: connected` once the
credentials are correct.

## Security used

- **bcrypt is necessary:** it hashes passwords before they are written to
  MySQL. Plain-text passwords are never stored.
- **JWT is necessary in this app:** login returns a token, and `/api/predict`
  can use that token when prediction access is added. Remove JWT only if no
  authenticated user session is needed.
