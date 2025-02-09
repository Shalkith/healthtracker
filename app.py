from flask import Flask, render_template,request,redirect
from scripts import duckdb_runner
from datetime import datetime




app = Flask(__name__)

@app.route("/",  methods=["GET", "POST"])
def main():
    if request.method == "GET":
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        #users = duckdb_runner.get_users()
        #health_log = duckdb_runner.get_health_log()
        con = duckdb_runner.connect()
        selections = duckdb_runner.get_data(con,'select * from selections')
        users = duckdb_runner.get_data(con,'select * from users')
        #print(selections)
        duckdb_runner.close_connection(con)
        return render_template('index.html',date = date, selections=selections,users=users)
    
    if request.method == "POST":
        con = duckdb_runner.connect()
        selection = request.form['option']
        user = request.form['name']
        date = request.form['date']
        duckdb_runner.insert_health_log(con,date,selection,user)
        duckdb_runner.close_connection(con)
        # redirect back to the index page
        return redirect("/")

        
    return render_template('index.html')

@app.route("/insert",  methods=["GET", "POST"])
def insert():
    if request.method == "GET":
        return render_template('insert.html')
    con = duckdb_runner.connect()
    selection = request.form['selection']
    duckdb_runner.insert_selection(con,selection)
    duckdb_runner.close_connection(con)
    return redirect("/")

@app.route("/addnewuser",  methods=["GET", "POST"])    
def addnewuser():
    if request.method == "GET":
        return render_template('addnew.html',option='user')
    con = duckdb_runner.connect()
    user = request.form['value']
    duckdb_runner.insert_user(con,user)
    duckdb_runner.close_connection(con)
    return redirect("/")

@app.route("/addnewselection",  methods=["GET", "POST"])    
def addnewselection():
    if request.method == "GET":
        return render_template('addnew.html',option='selection')
    con = duckdb_runner.connect()
    selection = request.form['value']
    duckdb_runner.insert_selection(con,selection)
    duckdb_runner.close_connection(con)
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80, threaded=True)