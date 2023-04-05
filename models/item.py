from db import db #To get the SQLAlchemy instance to item.py from db.py

#This instance have a bunch of things inside it that we can use, to later on tell SQLAlchemy
#what table we gonna use in our application and what columns those table we have
#In addition any class that we create that maps to a table with columns, SQLAlchemy would automatically be able to handle turning those table rows into Python object.

class ItemModel(db.Model): #this now becomes a mapping between a row in a table to a Python class and therefore Python object.
    __tablename__="items" #this tells SQL alchemy that we gonna use a table called items for this class and all the objects of the class

    id = db.Column(db.Integer,primary_key=True) #This is how we define a column that will be a part of the items table (its gonna be a integer column and its a primary key of the table)
    name = db.Column(db.String(80), unique=True,nullable=False) #You can take unique=True away if you want to have different store can have same items of the same name
    description =db.Column(db.String)
    price = db.Column(db.Float(precision=2),unique=False,nullable=False)
    store_id = db.Column(db.Integer,db.ForeignKey("stores.id"),unique=False,nullable=False) #store_id is the link between items table and stores table, db.ForeignKey(<table_name>.<column_which_acts_as_foreignkey>)
    #Every item has one store associated with it.

    store = db.relationship("StoreModel",back_populates="items") #Grab me a storemodel object that has this store_id
    tags = db.relationship("TagModel",back_populates="items",secondary="item_tags")