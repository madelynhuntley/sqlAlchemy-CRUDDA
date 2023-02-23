from sqlalchemy.dialects.postgresql import UUID
import uuid
from db import db


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