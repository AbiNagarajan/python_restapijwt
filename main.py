from flask import Flask, render_template, request, make_response   
from werkzeug.security import generate_password_hash, check_password_hash
import uuid 
import jwt
import datetime
import sqlite3

#code to create database 
# conn = sqlite3.connect('restapidatabasefinal.db')
# print ("Opened database successfully")

#code to create user details table.
# conn.execute('''CREATE TABLE userdet
#          (publiciden char(100)    NOT NULL,
#          emailid char(100) PRIMARY KEY    NOT NULL,
#          password char(100)     NOT NULL,
#          role char(50) NOT NULL);''')

#code to create itemslist table
# conn.execute('''CREATE TABLE "itemslist" (
# 	"Email"	TEXT NOT NULL,
# 	"Name"	TEXT NOT NULL,
# 	"Price"	REAL NOT NULL
# );''')
# print ("Table created successfully")



app = Flask(__name__) 

#secret key used while encoding jwt token
app.config['SECRET_KEY']='te$tre$tap1'

# initial page while the server starts
@app.route('/')
@app.route('/index')
def index():
    return render_template('firstpage.html')

# signup page rendered to register intially
@app.route('/signup', methods=['GET', 'POST'])
def signupfunc():
    return render_template('signup.html')

# login page rendered after registering
@app.route('/loginpage', methods=['GET', 'POST'])
def loginfunc():
    return render_template('login.html')

# view page to view the item details
@app.route('/view')
def viewdet1():
    return render_template('view.html', title='Home')
        
# enter the signup values into database
@app.route('/reg', methods=['GET', 'POST'])
def reg():
   try:
   
      if request.method == 'POST':
         
         emailiduser = request.form['email']
         passworduser = request.form['passwordentered']
         roleuser = request.form['radio1']
         hashed_password = generate_password_hash(passworduser, "sha256")
         publicid = str(uuid.uuid4())
         
         conn = sqlite3.connect('restapidatabasefinal.db')
         print ("Opened database successfully")
         params = (publicid,emailiduser,hashed_password,roleuser)
         conn.execute("INSERT INTO userdet (publiciden,emailid,password,role) VALUES " + str(params) + ";")
         
         conn.commit()
         conn.close()
         
      return render_template("firstpage.html")
   
   except:
      return render_template("bye1.html")


# login check and token is generated if the role is seller
@app.route('/login', methods=['GET', 'POST'])  
def login_user():
   try:
      if request.method == 'POST':
         
         emailidusercheck = request.form['emailuser1']
         passwordusercheck = request.form['passwordentered1']
      conn = sqlite3.connect('restapidatabasefinal.db')
      print ("Opened database successfully")
            
      data1 = conn.execute("SELECT publiciden,password,role from userdet where emailid='" +emailidusercheck+"';")
      rows = data1.fetchall()
      if check_password_hash(str(rows[0][1]),str(passwordusercheck)):
         
         if rows[0][2] == "seller":
            token = jwt.encode({'public_id': rows[0][0], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], )  
            resp = make_response(render_template('login1.html',id=emailidusercheck))
            resp.set_cookie('tokenimportant', token)
            conn.close()
            return resp

         else:
            return(render_template('important.html'))
            conn.close()

      else:
         return(render_template('bye.html'))
   except:
      return(render_template('bye.html'))

# view page action for the admil seller
@app.route('/viewdetails', methods=['GET', 'POST'])  
def viewde():
   try:
      conn = sqlite3.connect('restapidatabasefinal.db')
      print ("Opened database successfully")
      data2 = conn.execute("select * from itemslist;")
      rows = data2.fetchall(); 
      print(rows)
      conn.close()
      return render_template('view.html',rows = rows)
   except:
      return render_template('bye.html')


# view page action for the buyer
@app.route('/viewdetailsbuyer', methods=['GET', 'POST'])  
def viewdebuyer():
   try:

      conn = sqlite3.connect('restapidatabasefinal.db')
      print ("Opened database successfully")
      data3 = conn.execute("select Name,Price from itemslist;")
      rows3 = data3.fetchall(); 
      print(rows3)
      conn.close()
      return render_template('important.html',rows = rows3)
   except:
      return render_template('bye.html')

# insert items page is rendered 
@app.route('/insert')
def insert():
    return render_template('insert.html', title='Home')

# logout action for the seller and delete the cookie
@app.route('/logout')
def logout():
   tokencookie = request.cookies.get('tokenimportant')
   resp = make_response(render_template('firstpage.html'))
   resp.set_cookie('tokenimportant',tokencookie,max_age=0)
   return resp

# logout action for the buyer
@app.route('/logoutbuyer')
def logoutbuyer():
   resp = make_response(render_template('firstpage.html'))
   return resp

# insert item details in the database
@app.route('/insertdetail', methods=['GET', 'POST'])  
def insertdet():
   try:
      if request.method == 'POST':
         
         electname = request.form['elecname']
         electprice = request.form['elecprice']
         tokencookie = request.cookies.get('tokenimportant')
         tokenpubliciddata = jwt.decode(tokencookie, app.config['SECRET_KEY'])
         publicid_token = tokenpubliciddata['public_id']
         conn = sqlite3.connect('restapidatabasefinal.db')
         print ("Opened database successfully")
         dataemail = conn.execute("SELECT emailid from userdet where publiciden='" +publicid_token+"';")
         rows = dataemail.fetchall()
      
         params = (rows[0][0],electname,electprice)
         conn.execute("INSERT INTO itemslist (Email,Name,Price) VALUES " + str(params) + ";")
         
         conn.commit()
         conn.close()
         return(render_template('login1.html',id = rows[0][0]))
   except:
      return(render_template('bye2.html'))


# main method, since threaded is true can handle multiple user requests concurrently
# seperate thread is create for each user request
if  __name__ == '__main__':  
     app.run(debug=True, threaded=True)