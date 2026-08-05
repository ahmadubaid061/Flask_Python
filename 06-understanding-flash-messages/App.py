from flask import Flask,request,render_template,flash,redirect,url_for

app=Flask(__name__)

app.secret_key="my_secret_key"

@app.route("/",methods=["POST","GET"])
def form():
    if request.method=="POST":
        name=request.form.get("name")
        email=request.form.get("email")
        message=request.form.get("message")
        
        return render_template("welcome.html",name=name,email=email,message=message)
    return render_template("form.html")

if __name__=="__main__":
     app.run(debug=True)