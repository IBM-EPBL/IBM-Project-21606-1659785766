
from flask import Flask, render_template,request,flash,redirect,url_for,session
import ibm_db
import sendgrid
import os
from dotenv import load_dotenv
from sendgrid.helpers.mail import Mail, Email, To, Content


load_dotenv()
app = Flask(__name__)
app.secret_key="123"
# conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=rwc61888;PWD=kjMZoqMxzEKqkAAL",'','')
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=vmf90293;PWD=HJcZFhJh1CeBHfsH",'','')
cartproduct=[]
@app.route('/')
def index():
    stmt = "SELECT * FROM PRODUCT"
    sql = ibm_db.prepare(conn,stmt)
    ibm_db.execute(sql)
    dictionary = ibm_db.fetch_assoc(sql)
    print(dictionary)
    a=[]
    while dictionary != False:
        a.append(dictionary)
        print(dictionary)
        dictionary = ibm_db.fetch_assoc(sql)
    return render_template('homepage.html', product=a)

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        sql = "SELECT * FROM CUSTOMER WHERE email =? AND password = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:  
            session["name"]=account["NAME"]
            session["mail"]=account["EMAIL"]
            session["cart"]={'1':'abc'}
            # print(session)
            return redirect(url_for('index'))
        else:
            flash("INCORRECT USERNAME OR PASSWORD","danger")
    return render_template('login.html')


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
        
            password2= request.form['password2']
            name=request.form['name']
            password = request.form['password']
            mail=request.form['email']
            print(name) 
            if(len(password2)<1 or len(name)<1 or len(mail)<1):
                flash("Error in Insert Operation")
                return redirect(url_for('register'))
            if(password!=password2):
                flash("Password mismatch")
                return redirect(url_for('register'))
            sql = "SELECT * FROM CUSTOMER WHERE name =?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,name)
            ibm_db.execute(stmt)
            account = ibm_db.fetch_assoc(stmt)
            if account:
                return render_template('login.html',msg="Account already exists please login")
            insert_sql = "INSERT INTO CUSTOMER VALUES (?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, mail)
            ibm_db.bind_param(prep_stmt, 3, password2)
            ibm_db.execute(prep_stmt)

            flash("Account Created Successfully","Login to Continue")
            sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            from_email = Email("kylprakash420@gmail.com")  # Change to your verified sender
            to_email = To(mail)  # Change to your recipient
            subject = "Registration successful  "
            content = Content("text/plain", "You have successfully registered to the inventory management system for retailers as a customer, thank you - team Inventory Management System for Retailers")
            mail = Mail(from_email, to_email, subject, content)

            # Get a JSON-ready representation of the Mail object
            mail_json = mail.get()

            # Send an HTTP POST request to /mail/send
            response = sg.client.mail.send.post(request_body=mail_json)
            print(response.status_code)
            print(response.headers)
        except:
            flash("Error in Insert Operation","danger")

            

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/test',methods=['GET','POST'])
def test():
    
    stmt = "SELECT * FROM CUSTOMER"
    sql = ibm_db.prepare(conn,stmt)
    ibm_db.execute(sql)
    dictionary = ibm_db.fetch_assoc(sql)
    print(dictionary)
    a=[]
    while dictionary != False:
        a.append(dictionary)
        print(dictionary)
        dictionary = ibm_db.fetch_assoc(sql)
   
    
    return render_template('test.html')

@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    if request.method=='POST':
        try:
            productname = request.form['productname']
            productid = request.form['productid']
            quantity = int(request.form['quantity'])
            price = int(request.form['price'])
            imageurl = request.form['imageurl']
            insert_sql = "INSERT INTO PRODUCT VALUES (?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, productid)
            ibm_db.bind_param(prep_stmt, 2, productname)
            ibm_db.bind_param(prep_stmt, 3, quantity)
            ibm_db.bind_param(prep_stmt, 4, price)
            ibm_db.bind_param(prep_stmt, 5, imageurl)
            ibm_db.execute(prep_stmt)
            flash('Product added successfully')
            
        except:
            flash('An error occured while adding the product')
        finally:
            return redirect(url_for('addproduct'))
            
    return render_template('addproduct.html')

@app.route('/home')
def index1():
    stmt = "SELECT * FROM PRODUCT"
    sql = ibm_db.prepare(conn,stmt)
    ibm_db.execute(sql)
    dictionary = ibm_db.fetch_assoc(sql)
    print(dictionary)
    a=[]
    while dictionary != False:
        a.append(dictionary)
        # print(dictionary)
        dictionary = ibm_db.fetch_assoc(sql)
    return render_template("product.html",product=a)


@app.route('/cartadd',methods=['POST'])
def cartadd():
    id = request.form['id']
    quan = int(request.form['quantity'])
    if(not session.get('name')):
        flash('Log in or Register to buy products')
        return redirect(url_for('login'))
    if id and quan:
        stmt = "SELECT * FROM PRODUCT WHERE PRODUCTID=?"
        sql = ibm_db.prepare(conn,stmt)
        ibm_db.bind_param(sql,1,id)
        ibm_db.execute(sql)
        dictionary = ibm_db.fetch_assoc(sql)
        curquan = int(dictionary['QUANTITY']) - quan
        stmt = "UPDATE PRODUCT SET QUANTITY = ? WHERE PRODUCTID= ?"
        sql = ibm_db.prepare(conn,stmt)
        ibm_db.bind_param(sql,1,curquan)
        ibm_db.bind_param(sql,2,id)
        ibm_db.execute(sql)
        print("hh")
        flash('Product purchased successfully')
    # print( id,quan )
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
        return render_template("cart.html",products= cartproduct)




if __name__ == '__main__':
    app.run(debug=True)
