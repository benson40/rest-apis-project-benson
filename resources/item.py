from flask.views import MethodView #used for creating a class and the methods of the class route to specific endpoint.
from flask_smorest import Blueprint,abort
from flask_jwt_extended import jwt_required,get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items",__name__,description="Operations on items")

@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200,ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id) #it retrieves the item from the database using the items primary_key, if there is no item with this primary key then it will automatically abort with 404 status code.
        #no need to do any error handling,its all handled for you
        return item
    
        #We already have this code to get item based on item_id in app.py, so put it here.
        #Now, delete everything since we need to use the ItemModel
        '''
        try:
            return items[item_id] #If item_id is not there, then we get a key error
        except KeyError:
            abort(404,message="Item not found.")
        '''

    @jwt_required()
    def delete(self, item_id):
        #Similarly we do it for delete as well, we gonna add ItemModel.query.get_or_404(item_id)
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401,message="Admin privilege required.")

        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        
        return {"message":"Item deleted."}
        
        '''
        #We already have this code to delete item based on item_id in app.py, so put it here.
        try:
            del items[item_id]
            return {"message":"Item deleted."}
        except KeyError:
            abort(404, message="Item not found.")
        '''

    @blp.arguments(ItemUpdateSchema) #Order of decorators matters
    @blp.response(200,ItemSchema) #so make sure this is after the arguments decorator(i.e, deeper in the nesting of decorators)
    def put(self,item_data,item_id):
        item = ItemModel.query.get(item_id)
        #If an item doesn't exist, you should create it. And if it exists you should update it.
        if item: #If item exists, we need only price and name
            item.price = item_data["price"]
            item.name = item_data["name"]
        else: #If it doesnt exist, then we need price, name, store_id to be passed
            item = ItemModel(**item_data)

        db.session.add(item)
        db.session.commit()

        return item 
        

        #Idempotent request - running one or 10 requests should result in the same state at the end of it.
        '''
        Here we do the same thing as we did above in delete
        #no need of this anymore item_data = request.get_json()
        #whatever data client sends, it is passed through the ItemUpdateSchema, it checks and validates it and returns an argument (item_data) which is a validated dictionary

        #Here we use marshmallow schemas to do that validation, so we remove the if statement
        try:
            item = items[item_id]
            #Update the dictionary with the new dictionary update operator: |=
            item |= item_data  #merge update operator in dictionary

            return item
        except KeyError:
            abort(404, message="Item not found")
        
        '''


@blp.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200,ItemSchema(many=True)) #instance of item schema that gets created 
    def get(self):
        #return items.values() #and this will be turned into a list so just return items.values
        return ItemModel.query.all()

    @jwt_required(fresh=True) #now you cannot call this endpoint unless we send a jwt, fresh=True means now it requires a fresh token
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self,item_data):
        #Inserting data into database model using db.session.add(item) and db.session.commit()
        item = ItemModel(**item_data)

        try:
            db.session.add(item) #you can add multiple things
            db.session.commit()  #it will be written in the database file when we commit(saving to disk)

        except SQLAlchemyError:
            abort(500,message="An error occured while inserting the item.")

        return item 
    


        #json that client sends is pass through the ItemSchema , it checks that the fields are there and they are the valid types, then gives the method an argument which is the validated dictionary so we can remove request.get_json(), 
        #doing this also adds some more information as to whats expected to your Swagger UI documentation.
        
        # Here not only we need to validate data exists,
        # But also what type of data is passed. Price should be float,
        #we remove the if statement and use the marshmallow schemas for the validation
       
        #Addig another validation, to not to add item more than once.
        '''
        for item in items.values():
            
            if (
                item_data["name"] == item["name"]
                and item_data["store_id"] == item["store_id"]
            ):
                abort(400, message=f"Item already exists.")
        '''
        #This checking here we will be doing in the database side as well.
        #This is already been checked there, so we remove it from here
        #Since, we are working with ItemModel object instead of dictionaries so we remove the below code
        '''
        item_id = uuid.uuid4().hex #here also we create a item id using Universal Unique Identifier
        item = {**item_data,"id":item_id} #saves that id to a dictionary 
        items[item_id] = item #and uses that in our items dictionary
        '''


