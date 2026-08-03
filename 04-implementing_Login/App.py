from flask import Flask,render_template,request,Response,session,redirect,url_for,flash

app=Flask(__name__)
app.secret_key = 'anything_random_and_long'

# home(login) page
@app.route("/",methods=["GET","POST"])
def login():
    return render_template('login.html')

# when user submits login form 
@app.route('/submit', methods=["GET", "POST"])
def submit():
    if request.method=="POST":
        user_name=request.form.get("username")
        password=request.form.get("password")
        
        if user_name=="admin" and password=="123":
            session["user"]=user_name
            return redirect(url_for('welcome'))
        
        else:
            return Response('invalid credintials. Please try again', mimetype='text/plain')

# what happens in welcome page after login submit
@app.route('/welcome')
def welcome():
    
    if 'user' not in session:
        flash('Please login first!', 'error')
        return redirect(url_for('login'))

    return render_template('welcome.html',username=session['user'])

# when user wants to logout
@app.route('/logout')
def logout():
    session.pop('user',None)
    
    return redirect(url_for("login"))


if __name__=='__main__':
    app.run(debug=True,use_reloader=False)
