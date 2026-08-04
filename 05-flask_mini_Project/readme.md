# User Profile Management System

this project is a simple flask application that allows users to sign up and sign in to view their profiles. The application dynamically handles user profiles based on the information provided during sign-up.

## project structure:

05-flask_mini_Project/
User Profile Management System/
templates/
home.html
sign_in.html
sign_up.html
app.py

## project flow:

1. User visits the home page (home.html) and is presented with options to sign up or sign in.
2. If the user chooses to sign up, they are directed to the sign_up.html page where they can create a new account by providing their details (e.g., username, email, password).
3. Upon successful sign-up, the user is redirected to their profile page, which displays their information dynamically based on the data they provided during sign-up.
4. If the user chooses to sign in, they are directed to the sign_in.html page where they can enter their credentials to access their profile.
5. Upon successful sign-in, the user is redirected to their profile page, which displays their information dynamically based on the data they provided during sign-up.
6. If the user enters incorrect credentials during sign-in, they are shown an error message and prompted to try again.
7. if user wants to log out, they can click on the logout button, which will redirect them back to the home page.

## backend implementation:

1. The backend is implemented using Flask, a lightweight web framework for Python.
2. The app.py file contains the main application logic, including route definitions for handling user sign-up, sign-in, and profile display.
3. User data is stored in a simple in-memory data structure (e.g., a dictionary) for demonstration purposes. In a production application, a database would be used to persist user information.
4. The application uses Flask's session management to keep track of logged-in users and their profiles.
