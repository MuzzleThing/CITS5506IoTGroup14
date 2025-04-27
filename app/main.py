from app import app, socketio, db
from flask import render_template, redirect, url_for, flash
from app.forms import HomePageForm
from app.models import Item
from datetime import timedelta
from sqlalchemy import select

@app.get('/')
def openHomepage():
    form = HomePageForm()
    items = db.session.execute(select(Item).order_by(Item.id).limit(8)).scalars().all()
    if not items:
        items = []
    return render_template('homepage.html', form=form, items=items)

@app.post('/')
def recordItem():
    form = HomePageForm()
    if form.validate_on_submit():
        # if form.expiryDate.data:
        #     item = Item (name=form.name.data, quantity=form.quantity.data, date=form.date.data, expiry_date=form.expiryDate.data)
        # else:
        #     item = Item (name=form.name.data, quantity=form.quantity.data, date=form.date.data, expiry_date=form.date.data + timedelta(days=3))
        #     # TODO: more flexible expiry time
        expiry = form.expiryDate.data or form.date.data + timedelta(days=5)
        print("Debugging here:", form.date.data, expiry)
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