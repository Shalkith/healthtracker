from flask import Flask, render_template,request,redirect, Response, flash
#from scripts import duckdb_runner
from scripts import mariadb_runner
from datetime import datetime
import matplotlib.pyplot as plt
import io
import numpy as np

db_runner = mariadb_runner 


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flashing messages

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
        notes = request.form['notes']
        db_runner.insert_health_log(con,date,selection,user,notes)
        db_runner.close_connection(con)
        # redirect back to the index page
        flash(f"Added {selection} for {user} on {date}", "success")  
        
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
    flash(f"Added {selection}", "success")
    return redirect("/")

@app.route("/addnewuser",  methods=["GET", "POST"])    
def addnewuser():
    if request.method == "GET":
        return render_template('addnew.html',option='user')
    con = db_runner.connect()
    user = request.form['value']
    db_runner.insert_user(con,user)
    db_runner.close_connection(con)
    flash(f"Added {user}", "success")
    return redirect("/")

@app.route("/addnewselection",  methods=["GET", "POST"])    
def addnewselection():
    if request.method == "GET":
        return render_template('addnew.html',option='selection')
    con = db_runner.connect()
    selection = request.form['value']
    db_runner.insert_selection(con,selection)
    db_runner.close_connection(con)
    flash(f"Added {selection}", "success")
    return redirect("/")

@app.route("/stats/<user>",  methods=["GET", "POST"])
def stats(user):
    
    con = db_runner.connect()
    if request.method == "GET":
        #users = db_runner.get_data(con,'select * from users')
        stats = db_runner.get_data(con,f"select * from health_log where user = '{user}'")
        db_runner.close_connection(con)     
        return render_template('stats.html',users=user,stats=stats)


@app.route("/stats/",  methods=["GET", "POST"])
def getstats():
    con = db_runner.connect()
    if request.method == "GET":
        users = db_runner.get_data(con,'select * from users')
        db_runner.close_connection(con)     
        return render_template('get_user.html',users=users)


    return redirect("/")

@app.route("/flash")
def index():
    flash("This is a toast message!", "success")  # Flash message with a category
    return render_template("toast.html")

@app.route('/plot.png')
def plot():
    # Sample data (replace with your data)
    dates = ["2024-01-01", "2024-02-01", "2024-03-01"]
    weights = [180, 175, 170]

    plt.figure(figsize=(6,4))
    plt.plot(dates, weights, marker='o', linestyle='-')
    plt.xlabel("Date")
    plt.ylabel("Weight (lbs)")
    plt.title("Weight Over Time")

    # Save plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return Response(img.getvalue(), mimetype='image/png')

@app.route('/<user>/bar_chart.png')
def bar_chart(user):
    con = db_runner.connect()
    stats = db_runner.get_data(con,f"select * from health_log where user = '{user}' order by date asc")
    db_runner.close_connection(con)     
    data = {}
    data['dates'] = {}

    # Sample data (Dates and counts of instances for Carbs and Veggies)
    #dates = ["2024-01", "2024-02", "2024-03"]
    
    for row in stats:
        date = row[1]
        category = row[2]
        user = row[4]
        if date in data['dates']:
            if category in data['dates'][date]:
                data['dates'][date][category] += 1
            else:
                data['dates'][date][category] = 1
        else:
            data['dates'][date] = {category: 1}
    print(data)
    dates = list(data['dates'].keys())
    carbs = [data['dates'][date].get('Carbs', 0) for date in dates]
    veggies = [data['dates'][date].get('Veggies', 0) for date in dates]
    protein = [data['dates'][date].get('Protein', 0) for date in dates]
    # line plot this data
    print(dates)
    print(carbs)
    print(veggies)
    print(protein)


    #plt.figure(figsize=(10,4))
    # needs to be able to show all the data and dates
    plt.figure(figsize=(10,6))

    plt.plot(dates, carbs, marker='o', linestyle='-', label='Carbs')
    plt.plot(dates, veggies, marker='o', linestyle='-', label='Veggies')
    plt.plot(dates, protein, marker='o', linestyle='-', label='Protein')

    # order the x-axis
    plt.xticks(dates, rotation=45)


    
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.title(f"Category Counts for {user}")
    plt.legend()

    # Save plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()


    return Response(img.getvalue(), mimetype='image/png')

if __name__ == '__main__':
    print("Starting Flask app")
    app.run(debug=False, host='0.0.0.0', port=80, threaded=True)