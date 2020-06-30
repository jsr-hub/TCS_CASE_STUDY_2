from flask import Flask,render_template,redirect,request, url_for,flash,session
import yaml
from flask_mysqldb import MySQL
from datetime import datetime,date


loggedin=False



app=Flask(__name__)
mysql = MySQL(app)
app.secret_key = "super secret key"
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']


#@app.route('/',methods=['GET', 'POST'])



@app.route("/",methods=['GET', 'POST'])
def login():
    global loggedin
    if request.method == "POST":
        if not session.get('logged_in'):
            details = request.form
            userName = details['username']
            password = details['password']
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM userstore WHERE login = %s AND password = %s', (userName, password))
            account = cur.fetchone()
            mysql.connection.commit()
            cur.close()
            print(account)
            if account:
                session['loggedin'] = True
                session['username'] = account[0]
                session['timestamp']=datetime.now()
                session['message']="Logged In Successfully"
                loggedin=True
                return redirect('/Home')
            else:
                return render_template("01 Login Page.html")
        else:
            return "already loggedin"
    return render_template("01 Login Page.html")


@app.route('/Home')
def Home():
    global loggedin
    if loggedin==True:   
        return render_template("10 Home Page.html",name=session['username'],message=session['message'])
    else:
        return redirect('/')

@app.route('/Create_Patient',methods=['GET', 'POST'])
def Create_Patient():
    global loggedin
    session['message']=""
    if loggedin==True:        
        if request.method=="POST":
            ssn_id=request.form.get('ssn_id')
            patient_name=request.form.get('patient_name')
            patient_age=request.form.get('patient_age')
            date_of_admission=request.form.get('date_of_admission')
            bed_type=request.form.get('bed_type').split(' ')[0]
            address=request.form.get('address')
            city=request.form.get('city')
            state=request.form.get('state')
            cur = mysql.connection.cursor()
            print(address)
            z=cur.execute("SELECT * FROM patient WHERE ws_ssn= %s",[ssn_id])
            if(len(ssn_id)==9 and z==0):
                cur.execute("insert into patient(ws_ssn,ws_pat_name,ws_age,ws_adrs,ws_doj,ws_rtype,city,state,status) values (%s,%s,%s,%s,%s,%s,%s,%s,'Active')",(ssn_id,patient_name,patient_age,address,date_of_admission,bed_type,city,state))
                mysql.connection.commit()
                cur.close()
                session['message']="Patient Created Successfully"
                return redirect('/Home')
        return render_template('02 Create Patient.html')
    else:
        return redirect('/')


@app.route('/Update_Patient',methods=['GET', 'POST'])
def Update_Patient():
    session['message']=""
    global loggedin
    if loggedin==True:          
        if request.method=="POST":
            if "patient_id" in request.form:
                pid=request.form.get('pid')
                cur = mysql.connection.cursor()
                z=cur.execute("SELECT * FROM patient WHERE ws_pat_id= %s",[pid])
                if z>0:
                    cust = cur.fetchone()
                    print(cust[7])
                    return render_template('03 Update Patient.html',data=cust)
            else:
                ssn_id=request.form.get('ssn_id')
                if ssn_id !=None:
                    patient_name=request.form.get('patient_name')
                    patient_age=request.form.get('patient_age')
                    date_of_admission=request.form.get('date_of_admission')
                    bed_type=request.form.get('bed_type').split(' ')[0]
                    address=request.form.get('address')
                    city=request.form.get('city')
                    state=request.form.get('state')
                    cur = mysql.connection.cursor()
                    print(address)
                    queryres=cur.execute("SELECT * FROM patient WHERE ws_ssn= %s",[ssn_id])
                    if(len(ssn_id)==9 and queryres!=0):
                        fetchvalue=cur.fetchone()
                        cur.execute("update patient set ws_pat_name=%s,ws_age=%s,ws_adrs=%s,ws_doj=%s,ws_rtype=%s,city=%s,state=%s,status=%s where ws_ssn=%s",[patient_name,patient_age,address,date_of_admission,bed_type,city,state,fetchvalue[9],ssn_id])
                        mysql.connection.commit()
                        cur.close()
                        session['message']="Patient Updated Successfully"
                        return redirect('/Home')                        
                    else:
                        session['message']="No Patient Exists"
                        return redirect('/Home')                        

                else:
                    session['message']="No Patient Exists"
                    return redirect('/Home')                        
        return render_template('03 Update Patient.html',data=None)
    else:
        return redirect('/')


@app.route('/Delete_Patient',methods=['GET', 'POST'])
def Delete_Patient():
    session['message']=""
    global loggedin
    if loggedin==True:        
        if request.method=="POST":
            if "patient_id" in request.form:
                pid=request.form.get('pid')
                cur = mysql.connection.cursor()
                z=cur.execute("SELECT * FROM patient WHERE ws_pat_id= %s",[pid])
                if z>0:
                    cust = cur.fetchone()
                    print(cust)
                    return render_template('04 Delete Patient.html',data=cust)
            else:
                ssn_id=request.form.get('ssn_id')
                if ssn_id !=None:
                    cur = mysql.connection.cursor()
                    queryres=cur.execute("SELECT * FROM patient WHERE ws_ssn= %s",[ssn_id])
                    if(len(ssn_id)==9 and queryres!=0):
                        cur.execute("delete from patient where ws_ssn=%s",[ssn_id])
                        mysql.connection.commit()
                        cur.close()
                        session['message']="Patient Record Deleted Successfully"
                        return redirect('/Home')                        
                    else:
                        session['message']="No Patient Exists"
                        return redirect('/Home')                        

                else:
                    session['message']="No Patient Exists"
                    return redirect('/Home')                        

        return render_template('04 Delete Patient.html',data=None)
    else:
        return redirect('/')


@app.route("/View_Patient")
def View_Patient(data = None):
    session['message']=""
    global loggedin
    if loggedin==True:        
        cur = mysql.connection.cursor()
        cur.execute("Select * from patient where status= %s" , ("Active",))
        result=cur.fetchall()
        data=list(list())
        for x in result:
            data.append(list(x)) 
        return render_template("06 View Patients.html", data =data)
    else:
        return render_template('01 Login Page.html')

@app.route("/Search_Patient")
def Search_Patient(data = None):        
    session['message']=""
    global loggedin
    if loggedin==True:        
        cur = mysql.connection.cursor()
        entered_id= request.args.get('patient_id')
        if(entered_id):
            cur.execute("Select * from patient where ws_pat_id = " + str(entered_id) )
            result = cur.fetchone()
            if result:
                data = list(result)   
                return render_template("05 Search Patient.html", data = data)
            else:
                flash("No patient with that ID!")
                return redirect("/Search_Patient")
        return render_template("05 Search Patient.html", data=data)
    else:
        return redirect('/')
    
    
@app.route('/Patient_Med',methods=["GET","POST"])
def Patient_Med():
    session['message']=""
    global loggedin
    if loggedin==True:        
        if request.method == 'POST':
            if 'Get Patient Id' in request.form:
                patientDetails = request.form
                cur = mysql.connection.cursor()
                session['patient_id'] = patientDetails['patient_id']
                resultValue = cur.execute("select * from patient where ws_pat_id=%s",[patientDetails['patient_id']])
                if resultValue > 0:
                    patientDetails = cur.fetchone()
                    print(patientDetails)
                else:
                    flash("No patient with that ID!")
                    return redirect('/Patient_Med')
                resultValue = cur.execute("select  med_name,sum(ws_qty),med_rate,sum(ws_qty*med_rate) from track_medicines LEFT JOIN medicines_master ON track_medicines.ws_med_id=medicines_master.med_id where ws_pat_id=%s group by med_name ",[patientDetails[1]])
                if resultValue > 0:
                    med= cur.fetchall()
                    print(med)
                else:
                    flash("No Medicines with that ID!")
                    med=[]
                return render_template("07 Issue Medicine_a.html",user=patientDetails,med=med)
                cur.close()
                
            if 'Issue Medicine' in request.form:
                session['list_med']=[]
                session['updatelist_med']=[]
                return redirect('/Issue_Medicine')
            
        return render_template("07 Issue Medicine_a.html",user=None)
    else:
        return redirect('/')
    
    
@app.route('/Issue_Medicine',methods=["GET","POST"])
def Issue_Medicine():
    session['message']=""
    global loggedin
    if loggedin==True:        
        list_med=session['list_med']
        updatelist_med=session['updatelist_med']
        cur = mysql.connection.cursor()
        patient_id = session['patient_id'] 
        resultValue = cur.execute("select med_name from medicines_master")
        if resultValue > 0:
            med = [item[0] for item in cur.fetchall()]
            print(med)
        if request.method == 'POST':
            if 'add' in request.form:
                medDetails = request.form
                print(medDetails)
                cur = mysql.connection.cursor()
                resultValue = cur.execute("select * from medicines_master where med_name=%s",[medDetails['medicine']])
                if resultValue > 0:
                    fetched_med= cur.fetchone()
                    if (int(medDetails['quantity'])<fetched_med[2]):
                        print(cur.execute("update medicines_master set med_qty=med_qty-%s where med_name=%s",[medDetails['quantity'],medDetails['medicine']]))
                        mysql.connection.commit()
                        rate=int(medDetails['quantity'])*int(fetched_med[3])
                        list_med.append(tuple((str(medDetails['medicine']),int(medDetails['quantity']),fetched_med[3],rate)))
                        updatelist_med.append(tuple((patient_id,fetched_med[0],int(medDetails['quantity']))))
                        session['list_med']=list_med
                        session['updatelist_med']=updatelist_med
                        return render_template("07 Issue Medicine_b.html",medicine=med,issued_med=list_med)
                    else:
                        flash("Given quantity is not available!")
                        return render_template("07 Issue Medicine_b.html",medicine=med,issued_med=list_med)
            if 'Issue Medicine' in request.form:
                mySql_insert_query = """INSERT INTO track_medicines (ws_pat_id,ws_med_id,ws_qty) 
                               VALUES (%s, %s, %s) """
                cur.executemany(mySql_insert_query, updatelist_med)
                mysql.connection.commit()
                session['patient_id']=None
                session['list_med']=None
                session['updatelist_med']=None
                return redirect('/Patient_Med')
    
        return render_template("07 Issue Medicine_b.html",medicine=med)
    else:
        return redirect('/')
    

@app.route('/Patient_Diag',methods=["GET","POST"])
def Patient_Diag():
    session['message']=""
    global loggedin
    if loggedin==True:        
        if request.method == 'POST':
            if 'Get Patient Id' in request.form:
                patientDetails = request.form
                cur = mysql.connection.cursor()
                session['patient_id'] = patientDetails['patient_id']
                resultValue = cur.execute("select * from patient where ws_pat_id=%s",[patientDetails['patient_id']])
                if resultValue > 0:
                    patientDetails = cur.fetchone()
                    print(patientDetails)
                else:
                    flash("No patient with that ID!")
                    return redirect('/Patient_Diag')
                resultValue = cur.execute("select  diagn_name,sum(diagn_rate) from track_diagnostics LEFT JOIN diagnostics_master ON track_diagnostics.ws_diagn_id=diagnostics_master.diagn_id where ws_pat_id=%s group by diagn_name ",[patientDetails[1]])
                if resultValue > 0:
                    diag= cur.fetchall()
                    print(diag)
                else:
                    flash("No Medicines with that ID!")
                    diag=[]
                return render_template("08 Issue Diagnostics_a.html",user=patientDetails,diag=diag)
                cur.close()
                
            if 'Issue Medicine' in request.form:
                session['list_med']=[]
                session['updatelist_med']=[]
                return redirect('/Add_Diagnostics')
            
        return render_template("08 Issue Diagnostics_a.html",user=None)
    else:
        return redirect('/')
    

@app.route('/Add_Diagnostics',methods=["GET","POST"])
def Add_Diagnostics():
    session['message']=""
    global loggedin
    if loggedin==True:        
        list_med=session['list_med']
        updatelist_med=session['updatelist_med']
        cur = mysql.connection.cursor()
        patient_id = session['patient_id'] 
        resultValue = cur.execute("select diagn_name from diagnostics_master")
        if resultValue > 0:
            diag = [item[0] for item in cur.fetchall()]
            print(diag)
        if request.method == 'POST':
            if 'add' in request.form:
                medDetails = request.form
                print(medDetails)
                cur = mysql.connection.cursor()
                resultValue = cur.execute("select * from diagnostics_master where diagn_name=%s",[medDetails['diagnostics']])
                if resultValue > 0:
                    fetched_med= cur.fetchone()
                    list_med.append(tuple((medDetails['diagnostics'],fetched_med[2])))
                    updatelist_med.append(tuple((patient_id,fetched_med[0])))
                    session['list_med']=list_med
                    session['updatelist_med']=updatelist_med
                    return render_template("08 Issue Diagnostics_b.html",diag=diag,added_diag=list_med)
                
            if 'Diagnostics' in request.form:
                mySql_insert_query = """INSERT INTO track_diagnostics (ws_pat_id,ws_diagn_id) 
                               VALUES (%s, %s) """
                cur.executemany(mySql_insert_query, updatelist_med)
                mysql.connection.commit()
                session['patient_id']=None
                session['list_med']=None
                session['updatelist_med']=None
                return redirect('/Patient_Diag')
    
        return render_template("08 Issue Diagnostics_b.html",diag=diag)
    else:
        return redirect('/')
    

@app.route("/Generate_Bill",methods=['GET', 'POST'])
def Generate_Bill():
    session['message']=""
    global loggedin
    if loggedin==True:        
        if request.method=="POST":
            if "patient_id" in request.form:
               price=0
               pid = request.form['pid']
               cur = mysql.connection.cursor()
               cur.execute('SELECT * FROM patient WHERE ws_pat_id  = %s and status like "Active"', [pid])
               account = cur.fetchone()
               print(account)
               if account:
                   if account[6]=="General":
                       price=2000
                   elif account[6]=='Semi':
                       price=4000
                   else:
                       price=8000
                   nod=(date.today()- account[5]).days
                   nods=nod*price
                   mysql.connection.commit()
                   cur.close()
                   cur = mysql.connection.cursor()
                   cur.execute("select  med_name,sum(ws_qty),med_rate,sum(ws_qty*med_rate) from track_medicines LEFT JOIN medicines_master ON track_medicines.ws_med_id=medicines_master.med_id where ws_pat_id=%s group by med_name ",[pid])
                   result = cur.fetchall()
                   print(result)
                   cur.execute(" select  diagn_name,sum(diagn_rate) from track_diagnostics LEFT JOIN diagnostics_master ON track_diagnostics.ws_diagn_id=diagnostics_master.diagn_id where ws_pat_id=%s group by diagn_name ",[pid])
                   dia=cur.fetchall()
                   cur.execute("update patient set status=%s where ws_pat_id=%s",("discharged",pid))
                   mysql.connection.commit()
                   cur.close()
                   
                   return render_template("09 Billing System.html",account=account,nod=nod,nods=nods,med=result,dia=dia)
               else:
                   session['message']="No Active Patient with this id"
                   return redirect('/Home')
            if "con" in request.form:
                   session['message']="Patient has been Discharged"
                   return redirect('/Home')
              
        return render_template("09 Billing System.html",account=(),nod=0,nods=0,med=(),dia=())
    else:
        return redirect('/')

@app.route('/Logout')
def Logout():
    session['loggedin'] = False
    session['username'] = None
    session['timestamp']=None
    return redirect('/')
    


if __name__=="__main__":
    app.run(debug=True)