from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime

app = Flask(__name__)
props_stock = {}

DATA_FILE = "props_stock.json"

# Load and save functions
def load_data():
    global props_stock
    try:
        with open(DATA_FILE, "r") as f:
            props_stock = json.load(f)
    except FileNotFoundError:
        props_stock = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(props_stock, f, indent=4)

@app.route('/')
def index():
    return render_template_string('''
    <h1>Props Stock Management</h1>
    <form action="/add" method="post">
        <h3>Add Prop</h3>
        ID: <input name="prop_id"><br>
        Name: <input name="name"><br>
        Quantity: <input name="quantity" type="number"><br>
        <input type="submit" value="Add">
    </form>
    <form action="/loan" method="post">
        <h3>Loan Prop</h3>
        ID: <input name="prop_id"><br>
        Quantity: <input name="quantity" type="number"><br>
        Borrower: <input name="borrower"><br>
        <input type="submit" value="Loan">
    </form>
    <form action="/return" method="post">
        <h3>Return Prop</h3>
        ID: <input name="prop_id"><br>
        Quantity: <input name="quantity" type="number"><br>
        Borrower: <input name="borrower"><br>
        <input type="submit" value="Return">
    </form>
    <h3>Current Stock</h3>
    <ul>
    {% for pid, info in props.items() %}
        <li>ID: {{ pid }}, Name: {{ info['name'] }}, Total: {{ info['quantity'] }}, Loaned: {{ info['loaned'] }}, Available: {{ info['quantity'] - info['loaned'] }}</li>
    {% endfor %}
    </ul>
    ''', props=props_stock)

@app.route('/add', methods=['POST'])
def add_prop():
    prop_id = request.form['prop_id']
    name = request.form['name']
    quantity = int(request.form['quantity'])
    props_stock[prop_id] = {
        "name": name,
        "quantity": quantity,
        "loaned": 0,
        "history": []
    }
    save_data()
    return "Prop added.<br><a href='/'>Back</a>"

@app.route('/loan', methods=['POST'])
def loan_prop():
    prop_id = request.form['prop_id']
    quantity = int(request.form['quantity'])
    borrower = request.form['borrower']
    if prop_id in props_stock and props_stock[prop_id]['quantity'] - props_stock[prop_id]['loaned'] >= quantity:
        props_stock[prop_id]['loaned'] += quantity
        props_stock[prop_id]['history'].append({
            "action": "loan",
            "quantity": quantity,
            "borrower": borrower,
            "timestamp": datetime.now().isoformat()
        })
        save_data()
        return "Prop loaned.<br><a href='/'>Back</a>"
    else:
        return "Not enough props to loan.<br><a href='/'>Back</a>"

@app.route('/return', methods=['POST'])
def return_prop():
    prop_id = request.form['prop_id']
    quantity = int(request.form['quantity'])
    borrower = request.form['borrower']
    if prop_id in props_stock and props_stock[prop_id]['loaned'] >= quantity:
        props_stock[prop_id]['loaned'] -= quantity
        props_stock[prop_id]['history'].append({
            "action": "return",
            "quantity": quantity,
            "borrower": borrower,
            "timestamp": datetime.now().isoformat()
        })
        save_data()
        return "Prop returned.<br><a href='/'>Back</a>"
    else:
        return "Invalid return operation.<br><a href='/'>Back</a>"

if __name__ == '__main__':
    load_data()
    # Avoid using debug=True to prevent errors related to _multiprocessing in restricted environments
    app.run(debug=False)
