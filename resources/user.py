from flask.views import MethodView 
from flask_smorest import Blueprint,abort
from passlib.hash import pbkdf2_sha256  #SHA 256 is a hashing algorithm, to hash the password that client sends us
from flask_jwt_extended import create_access_token,create_refresh_token,get_jwt_identity, jwt_required, get_jwt #Access token is a combination of numbers and characters that we are going to generate in the server, we're going to send it to the client. (And only way to get this access token is by providing correct username and password)

from db import db
from blocklist import BLOCKLIST
from models import UserModel
from schemas import UserSchema

blp = Blueprint("Users",__name__,description="Operations on users")


#User registration endpoint
@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")
        
        user = UserModel(   
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"]) 
        ) #hash the password before sending to the database.

        db.session.add(user)
        db.session.commit()

        return {"message":"User created successfully."}, 201

#Login endpoint
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"],user.password):  #checks if the password that user sent us can be hashed exactly as the password already in the database, match or not
            access_token = create_access_token(identity=user.id,fresh=True)
            #a refresh token
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token":access_token,"refresh_token":refresh_token} #access_token in our case is JWT and it is encoded, so we can decode it.
        
        abort(401,message="Invalid credentials.")

#Endpoint for token refresh
@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user,fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token":new_token}


#Another endpoint for logging out
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out."}


#Get user via id and delete user via id
@blp.route("/user/<int:user_id>")
class User(MethodView):
    #To get user by his id
    @blp.response(200,UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    #To delete a user by his id
    def delete(self,user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message":"User deleted"},200
