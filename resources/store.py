import uuid
from flask import request
from flask.views import MethodView #used for creating a class and the methods of the class route to specific endpoint.
from flask_smorest import Blueprint,abort

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel
from schemas import StoreSchema

#A blueprint in flask_smorest is used to divide an API into mulltiple segments

#Create blueprint
blp = Blueprint("stores",__name__,description="Operations on stores")  #The name stores is going to be used later on to refer to if we ever wanna create a link between two blueprints


@blp.route("/store/<int:store_id>") #This connects flask_smorest with the below flask methodview, 
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self,store_id):   #so now if we make a get request, then this method will run
        store = StoreModel.query.get_or_404(store_id)
        return store
    
        '''
        We remove this code and usethe StoreModel.get_or_404(store_id)
        #Already the code for this we have in app.py for getting stores based on store_id
        try:
            return stores[store_id] #If that store_id doesn't exist, we get a key error
        except KeyError:
            abort(404,message="Store not found.")
        '''


    def delete(self,store_id): #so now if we send a delete request, then this method will run
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        
        return {"message":"Store deleted"}
        '''
        We remove this code and place the above code
        #Paste the code from app.py for deleting store and put it here
        try:
            del stores[store_id]
            return {"message":"Store deleted."}
        except KeyError:
            abort(404, message="Store not found.")
        '''


#Getting all stores and creating new store will go to another methodview since the route is different.
@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        #return stores.values()
        return StoreModel.query.all()
    
    @blp.arguments(StoreSchema)  #So, whenever client sends a data it passes through StoreSchema and it validates it and returns and argument that is a validated dictionary(which is in store_data)
    @blp.response(200,StoreSchema)
    def post(self,store_data):
        #Inserting data into database model using db.session.add(store) and then db.session.commit()
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        
        except IntegrityError:
            abort(
                400,
                message="A store with that a name already exists"
            )
        except SQLAlchemyError:
            abort(500,message="An error occured creating the store")

        return store
    
        '''
        Since, we are using objct instead of dictionary, and we can do the checking in database side we can remove these lines 
        #store_data = request.get_json() no need of this now, since we are using Marshmallow schemas
        #Now we add the Marchmallow schema, no need of if statement for validation, so we remove it
    
        #to check if store already exists
        for store in stores.values():
            if store_data["name"] == store["name"]:
                abort(400,message=f"Store already exists.")

        store_id = uuid.uuid4().hex  #To generate a univeral unique identifier, these are not random, u need to import uuid
        store = {**store_data,"id":store_id} #**store_data will unpack store_data dictionary values and put it in the new dictionary that is store.
        stores[store_id] = store
        '''
    ##Marshmallow can turn an object into json, just as it can turn a dictionary into json.
