from flask import Flask,render_template,flash,url_for,redirect,request
from forms import RegistrationForm

app=Flask(__name__)
app.secret_key="my_secret_key"

@app.route('/',methods=["GET","POST"])
def Register():
    form=RegistrationForm()
    if form.validate_on_submit():
        name=form.name.data
        email=form.email.data
        password=form.password.data
        #the password is stored in data base but  should not be displayed any where else
        #the database part goes here.....
        
        
        flash(f"Welcome {name} you have Registered Successfully!","success")
        return redirect(url_for("success"))
    # Only flash errors if the form was submitted (POST request) and validation failed
    elif request.method == 'POST' and not form.validate_on_submit():
        if form.errors:
            # Flash a general error message
            flash("Please correct the errors in the form.", "error")
            
    return render_template("form.html",form=form)

@app.route("/success")
def success():
    return render_template("success.html")



if __name__=="__main__":
    app.run(debug=True)