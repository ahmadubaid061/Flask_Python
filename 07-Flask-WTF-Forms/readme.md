# Flask-WTF Forms

A simple Flask application demonstrating form handling using Flask-WTF extension for form creation, validation, and CSRF protection.

## 📁 Project Structure

```
07-Flask-WTF-Forms/
├── templates/
│   ├── base.html
│   ├── form.html
│   └── success.html
├── App.py
├── forms.py
└── README.md
```

## 🚀 Quick Start

1. **Install dependencies:**

   ```bash
   pip install flask flask-wtf
   ```

2. **Run the application:**

   ```bash
   python App.py
   ```

3. **Open browser at:** `http://127.0.0.1:5000/`

## 📋 Features

- User registration form with validation
- Flash messages for success/error feedback
- CSRF protection
- Responsive design

## 📄 Files

- **App.py** - Main application with routes
- **forms.py** - Form class with validation rules
- **templates/** - HTML templates

## 🔧 Routes

| Route      | Methods   | Description       |
| ---------- | --------- | ----------------- |
| `/`        | GET, POST | Registration form |
| `/success` | GET       | Success page      |

## 🛠️ Customization

- Update `app.secret_key` in `App.py`
- Modify validators in `forms.py`
- Edit templates for different styling

## 📚 Learn More

[Flask-WTF Documentation](https://flask-wtf.readthedocs.io/)
