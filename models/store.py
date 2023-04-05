from db import db

class StoreModel(db.Model): #this now becomes a mapping between a row in a table to a Python class and therefore Python object.
    __tablename__="stores"

    id = db.Column(db.Integer,primary_key=True) #This id value here maps to store_id in items table
    name = db.Column(db.String(80),unique=True,nullable=False)

    #relating to the items model
    items = db.relationship("ItemModel",back_populates="store",lazy="dynamic", cascade="all, delete")
    tags = db.relationship("TagModel",back_populates="store",lazy="dynamic")
    #we use cascade above so that if a store is deleted, then all the items in that store is also deleted.
    

#But each store could have many items associated with it (One to Many relationship)
#A Store can have different items.