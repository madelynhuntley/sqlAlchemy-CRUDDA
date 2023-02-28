from sqlalchemy.dialects.postgresql import UUID
import marshmallow as ma
import uuid
from db import db
# from models.users import UsersSchema

class Organization(db.Model):
    __tablename__ = 'organizations'
    org_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(), nullable=False, unique=True)
    phone = db.Column(db.String())
    city = db.Column(db.String())
    state = db.Column(db.String())
    type = db.Column(db.String())
    active = db.Column(db.Boolean, nullable=False, default=True)

    users = db.relationship('Users', back_populates='organization' )


    def __init__(self, name, phone, city, state, type, active=True):
        self.name = name
        self.phone = phone
        self.city = city
        self.state = state
        self.type = type
        self.active = active

class OrganizationsSchema(ma.Schema):
    class Meta:
       fields = ('org_id', 'name', 'phone', 'city','state', 'type', 'users','active')

    users = ma.fields.Nested('UsersSchema', only=['user_id', 'first_name', 'last_name'], many=True)


org_schema = OrganizationsSchema()
orgs_schema = OrganizationsSchema(many=True)

class PublicOrgsSchema(ma.Schema):
    class Meta:
       fields = ['name','city','state', 'type']
 
public_schema = PublicOrgsSchema()
publics_schema = PublicOrgsSchema(many=True)
