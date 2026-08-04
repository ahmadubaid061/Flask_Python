from flask import Flask,render_template,request,Response,session,redirect,url_for

app=Flask(__name__)

users={
    'admin': {
        'username':'admin',
        'password':'123',
        'phone'   : '03111111111',
        'hobbies' : ['football','coding','chai'],
        'age'     : '24'
         }
}

# for user,userdata in users.items():
#     print(f"-------{user}----")
#     for key, values in userdata.items():
#         print(f"{key} : {values}")
   
@app.route("/")
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # check credentials against DB
        if username in users and users[username]['password'] == password:
          session['username'] = username
          return redirect(url_for('user_profile.html'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        phone=request.form.get('phone')
        hobbies=request.form.getlist('hobbies')
        age=request.form.get('age')
        
        # create new user in users
        users[username] = {
            'username': username,
            'password': password,
            'phone': phone,
            'hobbies': hobbies,
            'age': age
        }
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/user_profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = users.get(username)
    
    return render_template('profile.html', user=user)


@app.route('/logout')
def logout():
    session.pop("username",None)
    return redirect(url_for("login.html"))

if __name__ == '__main__':
    app.run(debug=True)