from flask import Flask, render_template,request,redirect, Response, flash
from scripts import mariadb_runner
from datetime import datetime
import numpy as np
import plotly.graph_objects as go
import io 
db_runner = mariadb_runner 


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flashing messages

@app.route("/",  methods=["GET", "POST"])
def main():
    
    if request.method == "GET":
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        con = db_runner.connect()
        selections = db_runner.get_data(con,'select * from selections')
        users = db_runner.get_data(con,'select * from users')
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
        stats = db_runner.get_data(con,f"select * from health_log where user = '{user}' order by date desc")
        db_runner.close_connection(con)     


        data = {}
        data['dates'] = {}
        categories = set()

        for row in stats:
            date = row[1]
            category = row[2]
            print(row)
            user = row[4]
            try:
                rowvalue = float(row[3])
            except:
                rowvalue = None
            categories.add(category)  # Collect unique categories
            if date in data['dates']:
                if category in data['dates'][date]:
                    #if value is not null, and its a number, sum it, else count it
                    if rowvalue is not None and isinstance(rowvalue, (int, float)):
                        data['dates'][date][category] += rowvalue
                    else:
                        data['dates'][date][category] += 1
                else:
                    #if value is not null, and its a number, sum it, else count it
                    if rowvalue is not None and isinstance(rowvalue, (int, float)):
                        data['dates'][date][category] = rowvalue
                    else:
                        data['dates'][date][category] = 1
            else:
                #if value is not null, and its a number, sum it, else count it
                if rowvalue is not None and isinstance(rowvalue, (int, float)):
                    data['dates'][date] = {category: rowvalue}
                else:
                    data['dates'][date] = {category: 1}

        dates = list(data['dates'].keys())
        carbs = [data['dates'][date].get('Carbs', 0) for date in dates]
        veggies = [data['dates'][date].get('Veggies', 0) for date in dates]
        protein = [data['dates'][date].get('Protein', 0) for date in dates]
        lbs = [data['dates'][date].get('Lbs', 0) for date in dates]

        # Create Plotly figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=carbs, mode='lines+markers', name='Carbs'))
        fig.add_trace(go.Scatter(x=dates, y=veggies, mode='lines+markers', name='Veggies'))
        fig.add_trace(go.Scatter(x=dates, y=protein, mode='lines+markers', name='Protein'))

        # Filter out zero values for weight (lbs)
        filtered_dates = [date for date, weight in zip(dates, lbs) if weight != 0]
        filtered_lbs = [weight for weight in lbs if weight != 0]
        fig.add_trace(go.Scatter(x=filtered_dates, y=filtered_lbs, mode='lines+markers', name='Weight (lbs)',yaxis='y2'))

        fig.update_layout(
            title=f"Category Totals for {user}",
            xaxis_title="Date & Time",
            yaxis=dict(title="Primary Axis Categories", side="left"),
            yaxis2=dict(
                title="Weight (lbs)", 
                side="right", 
                overlaying='y', 
                showgrid=False,
                range=[0, max(filtered_lbs) + 10],  # Adjust range as needed
            ),
            xaxis=dict(tickangle=-45, type="date"),  # Keep datetime format
            template="plotly_white",
            legend=dict(title="Category",
                        orientation="h",  # Set legend to be horizontal
                        x=0.5,  # Center the legend horizontally
                        xanchor="center",  # Anchor legend to the center
                        y=1.1,  # Move legend above the chart (1.1 pushes it up)
                        yanchor="bottom",  # Anchor legend to the bottom),
        ))

        # Convert Plotly figure to JSON
        graph_json = fig.to_json()

        #return render_template("chart.html", graph_json=graph_json)


        return render_template('stats.html',users=user,stats=stats,graph_json=graph_json)


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

if __name__ == '__main__':
    print("Starting Flask app")
    app.run(debug=False, host='0.0.0.0', port=80, threaded=True)