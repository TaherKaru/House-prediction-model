# House Price Prediction — Flask Backend

## Folder structure
```
backend/
  app.py                 # entry point — run this
  config.py               # settings (secret keys, DB, token expiry)
  extensions.py           # db, bcrypt, jwt, cors setup
  models.py               # User table
  routes/
    auth.py               # /api/auth/signup, /login, /me, /google
    predict.py             # /api/predict
  ml/
    train_model.py         # trains and saves model.pkl (run once)
    predict_utils.py       # loads model.pkl and predicts
    model.pkl               # created after you run train_model.py
  requirements.txt
  .env.example
```

## Setup

1. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   venv\Scripts\activate        (Windows)
   source venv/bin/activate     (Mac/Linux)
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your own secret keys.

3. Train the model (place your dataset as `ml/housing_data.csv` first):
   ```
   cd ml
   python train_model.py
   cd ..
   ```

4. Run the server:
   ```
   python app.py
   ```
   API runs at `http://localhost:5000`.

## Endpoints

| Method | Endpoint            | Auth required | Purpose                          |
|--------|----------------------|----------------|-----------------------------------|
| POST   | /api/auth/signup      | No             | Create a new account              |
| POST   | /api/auth/login       | No             | Log in, returns a JWT token       |
| GET    | /api/auth/me          | Yes            | Get current logged-in user        |
| POST   | /api/predict           | Yes            | Get a predicted house price       |

`/api/predict` expects JSON like:
```json
{ "area": 1200, "bedrooms": 3, "bathrooms": 2, "location": "Mumbai" }
```
and returns:
```json
{ "predicted_price": 8500000.0 }
```

## Connecting to your React (Vite) frontend

In your React `LoginPage.jsx`, replace the `handleSubmit` logic with a call to
the login API, and store the returned token (e.g. in `localStorage`):

```js
const res = await fetch("http://localhost:5000/api/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: values.email,
    password: values.password,
    remember: values.remember,
  }),
});
const data = await res.json();
if (res.ok) {
  localStorage.setItem("token", data.access_token);
  setSubmitted(true);
} else {
  setErrors({ password: data.error });
}
```

For the prediction form, send the JWT token in the `Authorization` header:
```js
fetch("http://localhost:5000/api/predict", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  },
  body: JSON.stringify({ area, bedrooms, bathrooms, location }),
});
```
