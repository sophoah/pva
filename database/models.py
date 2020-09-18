from .db import db
import datetime

class PVAParticipant(db.Document):
    emailaddress = db.StringField()
    validatoraddress = db.StringField(required=True, unique=True)
    ispops = db.StringField(required=True)
    ipaddress = db.StringField()
    validatorcreated = db.StringField(required=True)
    challenges = db.ListField(db.StringField())

class Result(db.Document):
    pvauser = db.ReferenceField(PVAParticipant, reverse_delete_rule=db.CASCADE)
    gamename = db.StringField(required = True) #uptime
    gameresult = db.IntField(required = True, default=0) #24

    meta = {
        'indexes': [{'fields': ('pvauser', 'gamename'), 'unique': True}]
    }   

# collection for storing historical validator data