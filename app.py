from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb://admin:secret@localhost:27017/?authSource=admin")
db = client["habit_tracker"]
habits = db["habits"]

@app.route('/')
def index():
    all_habits = list(habits.find())
    today = datetime.now().strftime("%Y-%m-%d")
    for h in all_habits:
        h['done_today'] = any(entry['date'] == today for entry in h.get("history", []))
    return render_template('index.html', habits=all_habits, today=today)

@app.route('/add', methods=['POST'])
def add_habit():
    name = request.form['name']
    if name:
        habits.insert_one({
            "name": name,
            "created_at": datetime.now(),
            "history": []
        })
    return redirect(url_for('index'))

@app.route('/mark/<habit_id>')
def mark_done(habit_id):
    from bson.objectid import ObjectId
    today = datetime.now().strftime("%Y-%m-%d")
    habit = habits.find_one({"_id": ObjectId(habit_id)})
    if habit and not any(entry['date'] == today for entry in habit.get("history", [])):
        habits.update_one({"_id": ObjectId(habit_id)}, {"$push": {"history": {"date": today}}})
    return redirect(url_for('index'))

@app.route('/delete/<habit_id>')
def delete_habit(habit_id):
    from bson.objectid import ObjectId
    habits.delete_one({"_id": ObjectId(habit_id)})
    return redirect(url_for('index'))

@app.route('/history/<habit_id>')
def habit_history(habit_id):
    from bson.objectid import ObjectId
    habit = habits.find_one({"_id": ObjectId(habit_id)})
    return render_template('habit.html', habit=habit)

if __name__ == '__main__':
    app.run(debug=True)

