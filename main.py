from flask import Flask, request
from pymongo import MongoClient

app = Flask(__name__)
# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']
menu_collection = db['menu']
orders_collection = db['orders']

# Helper function to generate HTML code for displaying the menu
def display_menu():
    menu_items = menu_collection.find()
    if menu_items.count_documents({}) > 0:
        table_rows = ""
        for dish in menu_items:
            table_rows += f"<tr><td>{dish['dish_id']}</td><td>{dish['name']}</td><td>{dish['price']}</td><td>{dish['availability']}</td></tr>"
        table_html = f"<table><thead><tr><th>Dish ID</th><th>Dish Name</th><th>Price</th><th>Availability</th></tr></thead><tbody>{table_rows}</tbody></table>"
        return f"<h2>Menu:</h2>{table_html}"
    else:
        return "<p>No dishes in the menu.</p>"

# Route for adding a new dish to the menu
@app.route('/menu/add', methods=['POST'])
def add_dish():
    dish = {
        'dish_id': request.form.get('dish_id'),
        'name': request.form.get('name'),
        'price': request.form.get('price'),
        'availability': request.form.get('availability')
    }

    # Check if all the required fields are provided
    if not dish['dish_id'] or not dish['name'] or not dish['price'] or not dish['availability']:
        return 'Please provide all the dish details.'

    # Insert dish into the database
    menu_collection.insert_one(dish)
    return 'Dish added successfully'

# Route for removing a dish from the menu
@app.route('/menu/remove/<dish_id>', methods=['POST'])
def remove_dish(dish_id):
    result = menu_collection.delete_one({'dish_id': dish_id})
    if result.deleted_count > 0:
        return 'Dish removed successfully.'
    else:
        return 'Dish not found.'

# Route for updating dish availability
@app.route('/menu/update/<dish_id>', methods=['POST'])
def update_availability(dish_id):
    availability = request.form.get('availability')
    result = menu_collection.update_one({'dish_id': dish_id}, {'$set': {'availability': availability}})
    if result.modified_count > 0:
        return 'Availability updated successfully.'
    else:
        return 'Dish not found.'

# Route for taking a new order
@app.route('/orders/place', methods=['POST'])
def place_order():
    customer_name = request.form.get('customer_name')
    dish_ids = request.form.get('dish_ids').split(',')
    ordered_dishes = []

    for dish_id in dish_ids:
        dish = menu_collection.find_one({'dish_id': dish_id, 'availability': 'yes'})
        if dish:
            ordered_dishes.append(dish)
        else:
            return f"Dish with ID {dish_id} is not available."

    order_count = orders_collection.count_documents({})
    order_id = order_count + 1

    order = {
        'order_id': order_id,
        'customer_name': customer_name,
        'dishes': ordered_dishes,
        'status': 'received'
    }
    orders_collection.insert_one(order)
    return f"Order {order_id} placed successfully."

# Route for updating order status
@app.route('/orders/update/<order_id>', methods=['POST'])
def update_order_status(order_id):
    status = request.form.get('status')
    result = orders_collection.update_one({'order_id': int(order_id)}, {'$set': {'status': status}})
    if result.modified_count > 0:
        return 'Order status updated successfully.'
    else:
        return 'Order not found.'

# Route for reviewing orders
@app.route('/orders')
def review_orders():
    orders = list(orders_collection.find())
    if len(orders) == 0:
        return 'No orders placed yet.'
    return orders


if __name__ == '__main__':
    app.run()
