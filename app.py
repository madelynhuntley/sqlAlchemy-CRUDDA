from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from models.users import Users, user_schema, users_schema

from models.organizations import Organization, org_schema, orgs_schema, publics_schema
import uuid
from db import db, init_db

app = Flask(__name__)

database_host = "127.0.0.1:5432"
database_name = "usermgt3"
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{database_host}/{database_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app,db)

def create_all():
    with app.app_context():
        db.create_all()

def is_valid_uuid(value):
    try: 
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False

# def get_user_from_object(user):
     
#      new_user_dict = {
#             'user_id':user.user_id,
#             'first_name':user.first_name,
#             'last_name':user.last_name,
#             'email':user.email,
#             'phone':user.phone,
#             'city':user.city,
#             'state':user.state,
#             'active':user.active
#         }
   
#      new_user_dict['organization'] = get_org_from_object(user.organization)
#      return new_user_dict

# def get_org_from_object(org):
#     return {
#         'org_id':org.org_id,
#         'name':org.name,
#         'phone':org.phone,
#         'city':org.city,
#         'state':org.state,
#         'active':org.active,
#         'type':org.type
#     }

def populate_object(obj, data_dictionary): 
    feilds = data_dictionary.keys()

    for feild in feilds:
        if hasattr(obj, feild):
            setattr(obj, feild, data_dictionary[feild])
    return obj

@app.route('/user/add', methods=['POST'])
def add_user():
    data = request.json
    email = data.get('email')

    user_email = bool(Users.query.filter_by(email=email).first())
    if user_email:
        return "Email already exists", 400
    
    if len(email) < 1:
        return "Email must be a non-empty string", 400

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')
    city = data.get('city')
    state = data.get('state')
    org_id = data.get('org_id')
    
    org_record = db.session.query(Organization).filter(Organization.org_id == org_id).first()

    if not org_record:
        return "Organization not found", 404
    
    if not is_valid_uuid(org_id):
        return "invalid org id", 400
    
    if len(phone) > 20:
        return "Phone number cannot be longer than 20 characters", 400

    new_user_record = Users(first_name, last_name, email, phone, city, state, org_id)
    db.session.add(new_user_record)
    db.session.commit()

    return jsonify(user_schema.dump(new_user_record)), 200


@app.route('/org/add', methods=['POST'])
def add_organization():
    data = request.json
    name = data.get('name')
    if not name or len(name) < 1:
        return jsonify("Name must be a non-empty string"), 400
    phone = data.get('phone')
    if len(phone) > 20:
        return "Phone number cannot be longer than 20 characters", 400
    city = data.get('city')
    state = data.get('state')
    type = data.get('type')

    new_org_record = Organization(name, phone, city, state, type)
    db.session.add(new_org_record)
    db.session.commit()

    return jsonify(org_schema.dump(new_org_record)), 201




@app.route('/user/get/<user_id>', methods=['GET'])
def get_by_id(user_id):
    if not is_valid_uuid(user_id):
        return "invalid id", 400
    
    user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

    if not user_record:
        return jsonify("User not found"), 404
    
    return jsonify(user_schema.dump(user_record)), 200


@app.route('/org/get/<org_id>', methods=['GET'])
def get_by_org_id(org_id):
    if not is_valid_uuid(org_id):
        return "invalid id", 400
    
    org_record = db.session.query(Organization).filter(Organization.org_id == org_id).first()

    if not org_record:
        return jsonify("Organization not found"), 404
    
    return jsonify(org_schema.dump(org_record)), 200
    
    # org_dict = get_org_from_object(org_record)
    # users = []
    # for u in org_record.users:
    #     users.append({
    #         'user_id': u.user_id,
    #         'first_name': u.first_name,
    #         'last_name': u.last_name
    #     })

        # org_dict['users'] = users
        # return jsonify(org_dict), 200

    
@app.route('/users/get', methods=['GET'])
def get_all_active_users():

    user_records = db.session.query(Users).filter(Users.active == True).all()
   
    if user_records: 
        return jsonify(users_schema.dump(user_records)), 200
    
        # users = []
        # for u in user_records:
        #     user_record = get_user_from_object(u)
        #     users.append(user_record)

    

    return 'No users found', 404


@app.route('/org/get', methods=['GET'])
def get_all_active_orgs():
    org_records = db.session.query(Organization).filter(Organization.active == True).all()
   
    if org_records: 
        # organizations = []
        # for o in org_records:
        #     org_record = get_org_from_object(o)
        #     org_record['num_users'] = len(o.users)
        #     organizations.append(org_record)

        return jsonify(orgs_schema.dump(org_records)), 200

    return 'No organizations found', 404


@app.route('/orgs/public', methods=['GET'])
def get_public_orgs():
    org_records = db.session.query(Organization).filter(Organization.active == True).all()
    
    if org_records:
        return jsonify(publics_schema.dump(org_records)), 200
    
    return jsonify('No public organizations found'), 404

# C - Create (/org/add)
# R - Read (/orgs/get, /org/get/<org_id>)
# U - Update (/org/update/<org_id>)
# D - Delete (/org/delete/<org_id>)
# D - Deactivate (/org/deactivate/<org_id>)
# A - Activate (/org/activate/<org_id>)


@app.route('/user/update/<user_id>', methods=['POST','PUT', 'PATCH'])
def user_update(user_id ):
    if not is_valid_uuid(user_id):
        return "invalid id", 400

    request_params = request.get_json()

    user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

    if user_record:
        if 'first_name' in request_params:
            user_record.first_name = request_params['first_name']
        if 'last_name' in request_params:
            user_record.last_name = request_params['last_name']
        if 'email' in request_params:
            user_record.email = request_params['email']
        if 'phone' in request_params:
            user_record.phone = request_params['phone']
        if 'city' in request_params:
            user_record.city = request_params['city']
        if 'state' in request_params:
            user_record.state = request_params['state']
        if 'org_id' in request_params:
            user_record.org_id = request_params['org_id']
        if 'active' in request_params:
            user_record.active = request_params['active']
            
        db.session.commit()

    return jsonify(user_schema.dump(user_record)), 200



@app.route('/org/update/<org_id>', methods=['PUT', 'POST', 'PATCH'])
def oranization_update(org_id):
    if not is_valid_uuid(org_id):
        return "invalid id", 400
    
    request_params = request.get_json()

    org_record = db.session.query(Organization).filter(Organization.org_id == org_id).first()

    if not org_record:
        return jsonify("Organization not found"), 404
    
    populate_object(org_record, request_params)
    db.session.commit()

    return jsonify (org_schema.dump(org_record)), 200



@app.route('/org/activate/<org_id>', methods=['PUT', 'POST', 'PATCH'])
def organization_activate_by_id(org_id):
    org_data = db.session.query(Organization).filter(Organization.org_id == org_id).first()

    if org_data:
        org_data.active = True
        db.session.commit()

        return jsonify(org_schema.dump(org_data)), 200

    return jsonify(f'Organization with org_id {org_id} Not Found'), 404


@app.route('/org/deactivate/<org_id>', methods=['PUT', 'POST', 'PATCH'])
def organization_deactivate_by_id(org_id):
    org_data = db.session.query(Organization).filter(Organization.org_id == org_id).first()

    if org_data:
        org_data.active = False
        db.session.commit()

        return jsonify(org_schema.dump(org_data)), 200

    return jsonify(f'Organization with org_id {org_id} Not Found'), 404


@app.route('/user/activate/<user_id>', methods=['PUT', 'POST', 'PATCH'])
def user_activate_by_id(user_id):
    user_data = db.session.query(Users).filter(Users.user_id == user_id).first()

    if not user_data:
        return jsonify(f"User with user_id {user_id} Not Found"), 404
    
    user_data.active = True
    db.session.commit()

    return jsonify(user_schema.dump(user_data)), 200



@app.route('/user/deactivate/<user_id>', methods=['PUT', 'POST', 'PATCH'])
def user_deactivate_by_id(user_id):

    user_data = db.session.query(Users).filter(Users.user_id == user_id).first()

    if user_data:
        user_data.active = False
        db.session.commit()

        return jsonify(user_schema.dump(user_data)), 200

    return jsonify(f'User with user_id {user_id} Not Found'), 404


@app.route('/user/delete/<user_id>', methods=['DELETE'])
def user_delete_by_id(user_id):

    user_data = db.session.query(Users).filter(Users.user_id == user_id).first()
    
    if user_data:
        db.session.delete(user_data)
        db.session.commit()
        return jsonify(f'User with user_id {user_id} deleted'), 201

    return jsonify(f'User with user_id {user_id} not found'), 404


@app.route('/org/delete/<org_id>', methods=['DELETE'])
def organization_delete_by_id(org_id):

    org_data = db.session.query(Organization).filter(Organization.org_id == org_id).first()
    
    if org_data:
        db.session.delete(org_data)
        db.session.commit()
        return jsonify(f'Organization with org_id {org_id} deleted'), 201

    return jsonify(f'Organization with org_id {org_id} not found'), 404
    

if __name__ == '__main__': 
    create_all()
    app.run(host='0.0.0.0', port=8086)