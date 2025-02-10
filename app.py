from flask import Flask, render_template,request,redirect
#from scripts import duckdb_runner
from scripts import mariadb_runner
from datetime import datetime

db_runner = mariadb_runner 


app = Flask(__name__)

@app.route("/",  methods=["GET", "POST"])
def main():
    if request.method == "GET":
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        #users = db_runner.get_users()
        #health_log = db_runner.get_health_log()
        con = db_runner.connect()
        selections = db_runner.get_data(con,'select * from selections')
        users = db_runner.get_data(con,'select * from users')
        #print(selections)
        db_runner.close_connection(con)
        return render_template('index.html',date = date, selections=selections,users=users)
    
    if request.method == "POST":
        con = db_runner.connect()
        selection = request.form['option']
        user = request.form['name']
        date = request.form['date']
        db_runner.insert_health_log(con,date,selection,user)
        db_runner.close_connection(con)
        # redirect back to the index page
        return redirect("/")

        
    return render_template('index.html')

@app.route("/insert",  methods=["GET", "POST"])
def insert():
    if request.method == "GET":
        return render_template('insert.html')
    con = db_runner.connect()
    selection = request.form['selection']
    db_runner.insert_selection(con,selection)
    db_runner.close_connection(con)
    return redirect("/")

@app.route("/addnewuser",  methods=["GET", "POST"])    
def addnewuser():
    if request.method == "GET":
        return render_template('addnew.html',option='user')
    con = db_runner.connect()
    user = request.form['value']
    db_runner.insert_user(con,user)
    db_runner.close_connection(con)
    return redirect("/")

@app.route("/addnewselection",  methods=["GET", "POST"])    
def addnewselection():
    if request.method == "GET":
        return render_template('addnew.html',option='selection')
    con = db_runner.connect()
    selection = request.form['value']
    db_runner.insert_selection(con,selection)
    db_runner.close_connection(con)
    return redirect("/")

if __name__ == '__main__':
    print("Starting Flask app")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)