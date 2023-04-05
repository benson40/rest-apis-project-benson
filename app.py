import os
import secrets

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db import db
from blocklist import BLOCKLIST
import models #Its similar as doing models.__init__ and inside it we have StoreModel and ItemModel

from resources.item import blp as ItemBlueprint #Importing blueprint of item from resources -> item.py
from resources.store import blp as StoreBlueprint #Importing blueprint of store from resources -> store.py
from resources.tag import blp as TagBlueprint #Importing blueprint of tag from resources -> tag.py
from resources.user import blp as UserBlueprint


#A factory pattern
def create_app(db_url=None):
    app = Flask(__name__) 

    #Some configurations
    app.config["PROPAGATE_EXCEPTIONS"]=True #tells if there are any exceptions propagate it to the main app so that we can see it
    app.config["API_TITLE"] = "Stores REST API" #Some flask smorest configuration, tells what title 
    app.config["API_VERSION"] = "v1" #what version it is
    app.config["OPENAPI_VERSION"] = "3.0.3" #standard for API, so we tell flask-smorest to use the version 3.0.3
    app.config["OPENAPI_URL_PREFIX"] ="/" #tells flask-smorest where the root of API is.
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui" #tells flask-smorest to use swagger for API documentation
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/" #this is where swagger code is there
    
    #Define database URL
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app) #Initializes the flask sqlalchemy extension, giving it our flask app so that it connects our flask app to sqlalchemy

    migrate = Migrate(app,db) #We are migrating app and db. So this has to be created after db.init_app(app)
    
    api = Api(app) #This basically connects the flask smorest extension to the flask app.

    #Set a secret key
    app.config["JWT_SECRET_KEY"] = "317024441450319040335035063301171231192" #used to verify whether this app generated the JWT when the user sends a request with JWT and check if its valid JWT that our API generated.
    #secrets.SystemRandom().getrandbits(128) generates a long and random secret key

    #Create an instance of JWT Manager
    jwt = JWTManager(app)

    #To check if token in blocklist
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    #What error messagethe user get specifically
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )
    

    @jwt.additional_claims_loader  #This lets you add extra information to JWT
    def add_claims_to_jwt(identity):
        # Look in the database and see whether the user is an admin
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader #This is returned when the JWT has expired
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    #Since we are using Flask_migrate to create our database tables, we no longer need SQLAlchemy to do it.
    # with app.app_context():
    #     db.create_all() #Whenever we start the app and before the first request is tackled it creates all the tables(only if it doesn't exist).

    #Register the blueprints with the API
    api.register_blueprint(ItemBlueprint)  #ItemBlueprint and StoreBlueprint are the blp variables that we defined in resources file.
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app









#Now since we connected flask smorest with our blueprints amnd all our endpoints, so now we got a Swagger page, this is kindf documentation that lets you try out the API
#Its available here: http://localhost:5005/swagger-ui

#Benefits of Flask-Smorest
#Not only it helps you to structure your code in a way that is easier to work with.
#It also gives you a lot more in terms of extra benefits,and swagger ui is one of those.







''' 
We'll be deleting(here we comment it out) all of this and use methodview, so we need to import that here

#Endpoints for Stores
#Get inforamtion about all stores
@app.get("/store") #http://127.0.0.1:5000/store
def get_stores(): 
    return {"stores":list(stores.values())}  #stores.values is not exactly a list, we need to convert it into a list


#Get a specific store using the store_id
@app.get("/store/<string:store_id>") #changed name to be a unique identifier
def get_store(store_id): #use store_id instead of name
    try:
        return stores[store_id] #If that store_id doesn't exist, we get a key error
    except KeyError:
        abort(404,message="Store not found.")


#Create a new store
@app.post("/store")
def create_store():
    #adding some error handling here
    #In future, we can do all of these much easily using other libraries.
    store_data = request.get_json() #changed  name to store_data instead of request_data
    if "name" not in store_data: #If name not there in the dictionary, then abort
        abort(
            400,
            message="Bad request. Ensure 'name' is included in the JSON payload."
        )
    #to check if store already exists
    for store in stores.values():
        if store_data["name"] == store["name"]:
            abort(400,message=f"Store already exists.")

    store_id = uuid.uuid4().hex  #To generate a univeral unique identifier, these are not random, u need to import uuid
    store = {**store_data,"id":store_id} #**store_data will unpack store_data dictionary values and put it in the new dictionary that is store.
    stores[store_id]=store
    return store, 201

#Delete Store
@app.delete("/store/<string:store_id>")
def delete_store(store_id):
    try:
        del stores[store_id]
        return {"message":"Store deleted."}
    except KeyError:
        abort(404, message="Store not found.")



#Endpoints for Items
#Get all items (this will look similar to get all stores, this thing we could not do earlier because all items were embedded in each store)
@app.get("/item")
def get_all_items():
    #return "Hello, world!" #If we changed our code, this new code when into our Docker container
    #the flask app refreshed because flaskenv is there, we got the new code here.
    return {"items":list(items.values())}


#Get a specific item using item_id
@app.get("/item/<string:item_id>")
def get_item(item_id):
    try:
        return items[item_id] #If item_id is not there, then we get a key error
    except KeyError:
        abort(404,message="Item not found.")


#Create a new item
@app.post("/item") #Now since we are not creating items inside of a specific store dictionary so we rename it as just /item
def create_item():
    item_data = request.get_json() 
    #adding some error handling
    # Here not only we need to validate data exists,
    # But also what type of data. Price should be float,
    # we gonna do that when we use marshmallow which is used for data validation
    if (
        "price" not in item_data
        or "store_id" not in item_data
        or "name" not in item_data
    ):
        abort(
            400,
            message="Bad request. Ensure 'price', 'store_id', and 'name' are included in the JSON payload."
        ) 
    #Addig another validation, to not to add item more than once.
    for item in items.values():
        if (
            item_data["name"] == item["name"]
            and item_data["store_id"] == item["store_id"]
        ):
            abort(400, message=f"Item already exists.")

    if item_data["store_id"] not in stores: #If that store id is not found in the dictionary then return no store found, with a 404 error message
        abort(404,message="Store not found.") #no need of return, abort will exit the request
    
    item_id = uuid.uuid4().hex #here also we create a item id using Universal Unique Identifier
    item = {**item_data,"id":item_id} #saves that id to a dictionary 
    items[item_id] = item #and uses that in our items dictionary
    
    return item,201


#Delete item
@app.delete("/item/<string:item_id>")
def delete_item(item_id):
    try:
        del items[item_id]
        return {"message":"Item deleted."}
    except KeyError:
        abort(404, message="Item not found.")


#Update item
@app.put("/item/<string:item_id>")
def update_item(item_id):
    item_data = request.get_json()
    if "price" not in item_data or "name" not in item_data:
        abort(400, message="Bad request. Ensure 'price' and 'name' are included in the JSON payload.")
    
    try:
        item = items[item_id]
        #Update the dictionary with the new dictionary update operator: |=
        item |= item_data

        return item
    except KeyError:
        abort(404, message="Item not found")

##Changes we made in the endpoints: added endpoints for deleting and updating item or a store
##Creating new endpoints
#Delete Store
@app.delete("/store/<string:store_id>")
def delete_store(store_id):
    try:
        del stores[store_id]
        return {"message":"Store deleted."}
    except KeyError:
        abort(404, message="Store not found.")


#Delete item
@app.delete("/item/<string:item_id>")
def delete_item(item_id):
    try:
        del items[item_id]
        return {"message":"Item deleted."}
    except KeyError:
        abort(404, message="Item not found.")

#Update item
@app.put("/item/<string:item_id>")
def update_item(item_id):
    item_data = request.get_json()
    if "price" not in item_data or "name" not in item_data:
        abort(400, message="Bad request. Ensure 'price' and 'name' are included in the JSON payload.")
    
    try:
        item = items[item_id]
        #Update the dictionary with the new dictionary update operator: |=
        item |= item_data

        return item
    except KeyError:
        abort(404, message="Item not found")

We'll be running the app in Docker instead of running it locally using flask run. 
Make some changes in the Docker file
COPY requirements.txt .  - Copy requirements.txt file into the current folder
RUN pip install -r requirements.txt -Run the pip install requirements.txt file which has the required packages names

Then build it using docker build -t flask-smorest-api .
Then run it: docker run -dp 5005:5000 flask-smorest-api - A container is running with the flask app
But the problem with this is, everytime you change your code, you have to rebuild and rerun so its not great

Instead, we gonna use a volume(-v): docker run -dp 5005:5000 -w /app -v "/c/Documents/yourproject:/app" flask-smorest-api

So, now we can make changes to our code and keep using our Docker container and we dont have to keep rebuilding and rerunning the app everytime.

When ur deploying ur app, you'll not use a volume because this is only for local development.

We will add flask smorest blueprints and method views
Then add Base Environment to Insomnia: http://127.0.0.1:5005, then now on for any request give {{url}} which turns to url (i.e, having http://127.0.0.1:5005).
This will ensure that if u ever update the url or the port no., you have to update in one place that is in the base environment.
'''

