from app import app, socketio, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import HomePageForm
from app.models import Item
from datetime import timedelta, date
from sqlalchemy import select,desc
import threading
import urllib.request
import json
import os

APIKey = "x8hfpalze3rcc8h1idminp3nwnjgmh" # The API key of a free trial account on BarcodeLookup.com
# In total there is 50 calls available, don't squander them

keyboardInput = ""

def listenToKeyboard():
    global keyboardInput
    while True:
        keyboardInput = input("You can scan an item or type a barcode here:")

# Function to handle barcode scanning in a separate thread
def listen_to_barcode_scanner():
    global keyboardInput
    while True:
        socketio.sleep(0.3)
        if keyboardInput != "":
            try:
                with app.app_context():
                    # Prompt for barcode input
                    barcode = keyboardInput
                    # print(f"barcode is {barcode}")
                    
                    # Construct the API URL
                    url = f"https://api.barcodelookup.com/v3/products?barcode={barcode}&formatted=y&key={APIKey}"
                    # print("url is made")
                    
                    # Make the API request
                    try:
                        with urllib.request.urlopen(url) as url_response:
                            data = json.loads(url_response.read().decode())
                            print("data retrived???")
                    except urllib.error.HTTPError as e:
                        if e.code == 404:
                            print(f"No entry found for barcode {barcode}.")
                            socketio.emit("itemNotFound", {"message": "The item which you scanned is not yet included in Barcode Lookup Database!\nPlease record this item manually."})
                        else:
                            print(f"HTTP error occurred: {e}")
                        keyboardInput = ""
                        continue
                    except Exception as e:
                        print(f"Error retrieving data: {e}")
                        keyboardInput = ""
                        continue
                    
                    itemName = data["products"][0]["title"]

                    # Store the scanned item into the database
                    item = Item (name=itemName, quantity=1, date=date.today(), expiry_date=date.today()+timedelta(weeks=4))
                    # Defaulf date is set to current day and expiry date is 4 weeks later
                    db.session.add(item)
                    db.session.commit()

                    # Ensure the directory exists
                    image_directory = "app/static/images"
                    os.makedirs(image_directory, exist_ok=True)  # Create the directory if it doesn't exist

                    # Download the image for the scanned item
                    image_filename = f"{itemName}.jpg"  # Save the image with the barcode as the filename
                    image_path = os.path.join(image_directory, image_filename)  # Save to the static/images directory
                    if not os.path.exists(image_path):  # Check if the file already exists
                        image_url = data["products"][0]["images"][0]  # Get the first image URL
                        urllib.request.urlretrieve(image_url, image_path)
                        print(f"Image downloaded and saved to {image_path}")
                    else:
                        print(f"Image already exists at {image_path}, skipping download.")

                    # Emit a WebSocket event to notify clients
                    # When a item is scanned and stored into database, every currently opened page should reload
                    print("Preparing to emit reload_page event...")
                    socketio.emit('reload_page', {'message': 'A new item has been scanned!'}, include_self=True)
                    print("Page reload event emitted.")
            
            except Exception as e:
                print(f"Error processing barcode: {e}")
            keyboardInput = ""



# Function to listen for "refresh" command in the terminal
def listen_for_refresh_command():
    print("listen_for_refresh_command started")
    global keyboardInput
    # command = keyboardInput
    while True:
        try:
            # command = input("Type 'refresh' to reload the page: ").strip().lower()
            if keyboardInput == "refresh":
                print("Refresh command received. Reloading page...")
                # with app.app_context():  # Ensure the correct app context
                socketio.emit('reload_page', {'message': 'Page refresh triggered!'}, include_self=True)
                print("Page reload event emitted.")
                keyboardInput = ""
            # print("sleeping")
            socketio.sleep(0.1)

        except Exception as e:
            print(f"Error in refresh command listener: {e}")

def test_background_task():
    try:
        while True:
            print("Test background task running...")
            socketio.sleep(1)
    except Exception as e:
        print(f"Error in test_background_task: {e}")

@socketio.on('connect')
def handleConnect():
    print("Client connected")

# Routes and view functions start here
currentDate = date.today()

@app.route('/test_reload')
def test_reload():
    print("Emitting test reload_page event...")
    socketio.emit('reload_page', {'message': 'Test reload triggered!'}, include_self=True)
    return "Test reload event emitted"

@app.get('/')
def openHomepage():
    form = HomePageForm()
    order = request.args.get('order', 'newest')  # Default to 'newest' if no argument is provided
    items_query = select(Item)
    if order == 'newest':
        items_query = items_query.order_by(desc(Item.id))
    elif order == 'oldest':
        items_query = items_query.order_by(Item.id)
    elif order == 'expiring':
        items_query = items_query.order_by(Item.expiry_date)
    items = db.session.execute(items_query.limit(8)).scalars().all()

     # Check if the image exists for each item
    for item in items:
        image_path = os.path.join("app/static/images", f"{item.name}.jpg")
        item.has_image = os.path.exists(image_path)
        
    return render_template('homepage.html', form=form, items=items, currentPage='homepage', currentDate=currentDate, order=order)

@app.post('/')
def recordItem():
    form = HomePageForm()
    if form.validate_on_submit():
        expiry = form.expiryDate.data or form.date.data + timedelta(days=5) # Expiry dates need to be more specific
        # print("Debugging here:", form.date.data, expiry)
        item = Item (name=form.name.data, quantity=form.quantity.data, date=form.date.data, expiry_date=expiry)
        db.session.add(item)
        db.session.commit()
        flash("Item recorded sucessfully", "success")
    else:
        flash("Error: please check your input again.", "error")
    return redirect(url_for('openHomepage'))

@app.get('/inventory')
def openInventory():
    form = HomePageForm()
    order = request.args.get('order', 'newest')  # Default to 'newest' if no argument is provided
    items_query = select(Item)
    if order == 'newest':
        items_query = items_query.order_by(desc(Item.id))
    elif order == 'oldest':
        items_query = items_query.order_by(Item.id)
    elif order == 'expiring':
        items_query = items_query.order_by(Item.expiry_date)
    items = db.session.execute(items_query).scalars().all()
    return render_template('inventory.html', form=form, items=items, currentPage='inventory', currentDate=currentDate, order=order)

@app.get('/deleteInventory')
def deleteItem():
    itemId = request.args.get('id')
    entry = db.session.execute(select(Item).where(Item.id==itemId)).scalar_one_or_none()
    if entry:
        db.session.delete(entry)
        db.session.commit()
        flash("Item is successfully deleted.", "success")
    else:
        flash("Error: Item not found!", "error")
    return redirect(url_for('openInventory'))

@app.post('/inventory')
def editItem():
    itemId = request.args.get('id')
    entry = db.session.execute(select(Item).where(Item.id==itemId)).scalar_one_or_none()
    form = HomePageForm()
    if form.validate_on_submit():
        if entry:
            entry.name = form.name.data
            entry.quantity = form.quantity.data
            entry.date = form.date.data
            entry.expiry_date = form.expiryDate.data
            db.session.commit()
            flash("Item is successfully edited.", "success")
        else:
            flash("Error: Item not found!", "error")
    else:
        flash("Error: the form is submitted with invalid field(s)", "error")
    return redirect(url_for('openInventory'))
# Routes and view functions end here


if __name__ == '__main__': # Run the server by command line: python -m app.main

    socketio.start_background_task(listen_to_barcode_scanner)

    keyboardInputThread = threading.Thread(target=listenToKeyboard, daemon=True)
    keyboardInputThread.start()

    socketio.run(app, debug=True) 
    # Format to specify IP and port: socketio.run(app, host="0.0.0.0", port=5000, debug = True)
    # the address is http://127.0.0.1:5000