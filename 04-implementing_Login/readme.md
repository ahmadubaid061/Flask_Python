# Implementing Login - Flask Application

---

## 📁 Folder Structure

```
04-implementing-login/
├── templates/
│   ├── login.html
│   └── welcome.html
├── App.py
└── README.md
```

## 🚀 Features

- User login with username and password
- Session-based authentication
- Protected welcome page (redirects to login if not authenticated)
- Logout functionality
- Flash messages for error handling

## 🔧 Installation

1. Make sure you have Python installed
2. Install Flask:

```bash
pip install flask
```

## ▶️ How to Run

1. Navigate to this folder:

```bash
cd 04-implementing-login
```

2. Run the Flask application:

```bash
python App.py
```

3. Open your browser and go to:

```
http://127.0.0.1:5000
```

## 📝 Usage

### Default Credentials

- **Username:** `admin`
- **Password:** `123`

### Login Flow

1. Enter credentials on the login page
2. Click "Login" to submit
3. If correct → redirected to welcome page
4. If incorrect → see error message
5. Click "Logout" to end session

## 📄 Pages

- **Login Page** (`/`): Login form
- **Welcome Page** (`/welcome`): Protected page visible only after login
- **Logout** (`/logout`): Ends user session

## ⚠️ Note

This is a basic demo for educational purposes. In production:

- Use proper password hashing (e.g., bcrypt)
- Use environment variables for secret keys
- Implement proper database authentication
- Add CSRF protection

## 📚 Learning Topics

- Flask session management
- Form handling (GET/POST)
- Route protection
- Template rendering with Jinja2
- Flash messages
