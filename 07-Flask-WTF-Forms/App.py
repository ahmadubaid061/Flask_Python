from flask import Flask,render_template,flash,url_for,redirect
from forms import RegistrationForm

app=Flask(__name__)
app.secret_key="my_secret_key"

@app.route('/',methods=["GET","POST"])
def Register():
    form=RegistrationForm()
    if form.validate_on_submit:
        name=form.name.data
        email=form.email.data
        password=form.password.data
        #the password is stored in data base but  should not be displayed any where else
        #the database part goes here.....
        
        
        flash(f"Welcome {name} you have Registered Successfully!","success")
        return redirect(url_for("success"))
    return render_template("form.html",form=form)

