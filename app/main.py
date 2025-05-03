from app import app, socketio, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import HomePageForm
from app.models import Item
from datetime import timedelta, date
from sqlalchemy import select,desc

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
    currentDate = date.today()
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


if __name__ == '__main__': # Run the server by command line: python main.py
    socketio.run(app, debug=True) 
    # Format to specify IP and port: socketio.run(app, host="0.0.0.0", port=5000, debug = True)