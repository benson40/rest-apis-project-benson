#We write our marshmallow schemas here
from marshmallow import Schema, fields

#We have defined the schema,
#Now we gonna rename this to PlainItemSchema and remove store_id
"""
class ItemSchema(Schema):
    id = fields.Str(dump_only=True) #we only want to use it when returning data
    name = fields.Str(required=True) #because it is something we recieve in the JSON payload of a request
    price = fields.Float(required=True)
    store_id = fields.Str(required=True)

    #It will check the fields that have required=True are there or not and the price is a float or not.
"""
class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True) #we only want to use it when returning data
    name = fields.Str(required=True) #because it is something we recieve in the JSON payload of a request
    price = fields.Float(required=True)
    

class ItemUpdateSchema(Schema):
    #When we update, we need to make sure that name and price are there.
    name = fields.Str() 
    price = fields.Float()  #they dont have to send both price and name
    store_id = fields.Int()
    
#Similarly we gonna change it to PlainStoreSchema
"""
class StoreSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
"""
class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

#We gonna use this schemas for validating data and for turning outgoing data into valid data as per the schema
#Now we have more validation
class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True,load_only=True) #only used when client sends some data
    store = fields.Nested(PlainStoreSchema(),dump_only=True) #this will be used only when returning data from client
    tags = fields.List(fields.Nested(PlainTagSchema()),dump_only=True)

class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()),dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema),dump_only=True)

class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(),dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()),dump_only=True)

class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)
    

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True,load_only=True)