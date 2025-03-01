from datetime import datetime
import random
from flask import Flask, jsonify, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields
from .utilities import Utility

import os
import uuid
import logging

standardize_response = Utility.standardize_response


# Initialize Flask app and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'mysql+pymysql://root:rootpassword@db:3306/PickADateDB'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

db = SQLAlchemy(app)

api = Api(app)

# log to console
logging.basicConfig(level=logging.DEBUG)

# Import models after initializing db to avoid circular import
from .models import Date, Event, User

event_create_model = api.model('EventCreate', {
    'event_name': fields.String,
    'description': fields.String,
    'max_date': fields.Date,
    'min_date': fields.Date,
    'lon': fields.Float,
    'lat': fields.Float
})

event_model = api.model('Event', {
    'event_id': fields.Integer,
    'event_name': fields.String,
    'description': fields.String,
    'date_created': fields.DateTime,
    'max_date': fields.Date,
    'min_date': fields.Date,
    'lon': fields.Float,
    'lat': fields.Float,
    'uuid': fields.String,
    'is_active': fields.Boolean
})

events_ns = api.namespace('events', description='Events related operations')
api.add_namespace(events_ns)

@events_ns.route('/event')
class event(Resource):
    @events_ns.expect(event_create_model)
    def post(self):
        try:
            data = request.get_json()

            max_date = datetime.strptime(data['max_date'], '%Y-%m-%d').date()
            min_date = datetime.strptime(data['min_date'], '%Y-%m-%d').date()

            event = Event.create(
                event_name=data['event_name'],
                description=data['description'],
                max_date=max_date,
                min_date=min_date,
                lon=data['lon'],
                lat=data['lat'],
                uuid=str(uuid.uuid4())
            )
            db.session.commit()
            return standardize_response(
                status='success',
                data=event.to_dict(),
                message='Event created successfully',
                code=201
            )
        except Exception as e:
            current_app.logger.exception(e)
            return standardize_response(
                status='error',
                message='An error occurred while creating the event',
                code=500
            )
    
    # takes url parameter of uuid
    @events_ns.doc(params={'uuid': 'UUID of the event'})
    def get(self):
        try:
            uuid = request.args.get('uuid')
            event = Event.get_event_by_uuid(uuid)
            if not event:
                return standardize_response(
                    status='error',
                    message='Event not found',
                    code=404
                )
            return standardize_response(
                status='success',
                data=event.to_dict(),
                message='Event retrieved successfully',
                code=200
            )
        except Exception as e:
            current_app.logger.exception(e)
            return standardize_response(
                status='error',
                message='An error occurred while retrieving the event',
                code=500
            )
        
user_create_model = api.model('UserCreate', {
    'event_id': fields.Integer,
    'name': fields.String,
    'phone': fields.String,
    'lat': fields.Float,
    'lon': fields.Float,
    'is_driver': fields.Boolean
})

users_ns = api.namespace('users', description='Users related operations')
api.add_namespace(users_ns)
        
@users_ns.route('/user')
class user(Resource):
    @users_ns.expect(user_create_model)
    def post(self):
        try:
            data = request.get_json()
            user = User.create(
                event_id=data['event_id'],
                name=data['name'],
                phone=data['phone'],
                lat=data['lat'],
                lon=data['lon'],
                icon_path='default.png',
                # generate random color
                color='#' + '%06x' % random.randint(0, 0xFFFFFF),
                is_driver=data['is_driver']
            )
            db.session.commit()
            return standardize_response(
                status='success',
                data=user.to_dict(),
                message='User created successfully',
                code=201
            )
        except Exception as e:
            current_app.logger.exception(e)
            return standardize_response(
                status='error',
                message='An error occurred while creating the user',
                code=500
            )
    
    # takes url parameter of event_id
    @users_ns.doc(params={'event_id': 'ID of the event',
                          'phone': 'Phone of the user',
                          'date': 'Date of the event (YYYY-MM-DD)'})
    def get(self):
        try:
            # if event_id and phone are provided, return the user
            if 'event_id' in request.args and 'phone' in request.args:
                event_id = request.args.get('event_id')
                phone = request.args.get('phone')
                user = User.get_user_by_phone_and_event_id(event_id=event_id, phone=phone)
                if not user:
                    return standardize_response(
                        status='error',
                        message='User not found',
                        code=404
                    )
                return standardize_response(
                    status='success',
                    data=user.to_dict(),
                    message='User retrieved successfully',
                    code=200
                )
            # if event_id is provided, return all users for the event
            elif 'event_id' in request.args:
                event_id = request.args.get('event_id')
                users = User.get_users_by_event_id(event_id)
                if not users:
                    return standardize_response(
                        status='error',
                        message='Users not found',
                        code=404
                    )
                return standardize_response(
                    status='success',
                    data=[user.to_dict() for user in users],
                    message='Users retrieved successfully',
                    code=200
                )
            # if date_id is provided, return the users for the date
            elif 'date' in request.args:
                date = request.args.get('date')
                users = User.get_users_by_date(date)
                if not users:
                    return standardize_response(
                        status='error',
                        message='Users not found',
                        code=404
                    )
                return standardize_response(
                    status='success',
                    data=[user.to_dict() for user in users],
                    message='Users retrieved successfully',
                    code=200
                )
            else:
                return standardize_response(
                    status='error',
                    message='Invalid request',
                    code=400
                )
        
        except Exception as e:
            current_app.logger.exception(e)
            return standardize_response(
                status='error',
                message='An error occurred while retrieving the users',
                code=500
            )
        

dates_ns = api.namespace('dates', description='Dates related operations')
api.add_namespace(dates_ns)

date_create_model = api.model('DateCreate', {
    'event_id': fields.Integer,
    'user_id': fields.Integer,
    'date': fields.DateTime,
    'is_blocked': fields.Boolean
})

date_delete_model = api.model('DateDelete', {
    'date_id': fields.Integer,
    'user_id': fields.Integer
})

@dates_ns.route('/date')
class date(Resource):

    @dates_ns.expect(date_create_model)
    def post(self):
        try:
            data = request.get_json()

            d = datetime.strptime(data['date'], '%Y-%m-%d').date()

            date = Date.create(
                event_id=data['event_id'],
                user_id=data['user_id'],
                date=d,
                is_blocked=data['is_blocked']
            )
            db.session.commit()
            return standardize_response(
                status='success',
                data=date.to_dict(),
                message='Date created successfully',
                code=201
            )
        except Exception as e:
            current_app.logger.exception(e)
            return standardize_response(
                status='error',
                message='An error occurred while creating the date',
                code=500
            )
        
    @dates_ns.expect(date_delete_model)
    def delete(self):
        try:
            data = request.get_json()
            if 'date_id' not in data or 'user_id' not in data:
                return standardize_response(
                    status='error',
                    message='Invalid request',
                    code=400
                )
            date_id = data['date_id']
            user_id = data['user_id']
            Date.delete(date_id, user_id)
            return standardize_response(
                status='success',
                message='Date deleted successfully',
                code=200
            )
        except Exception as e:
            current_app.logger.exception(e)
            return standardize_response(
                status='error',
                message='An error occurred while deleting the date',
                code=500
            )
    
    
    @dates_ns.doc(params={'event_id': 'ID of the event',
                          'user_id': 'ID of the user'})
    def get(self):
        try:
            # if only event_id is provided, return all dates for the event
            if 'event_id' in request.args:
                event_id = request.args.get('event_id')
                dates = Date.get_dates_by_event_id(event_id)
                if not dates:
                    return standardize_response(
                        status='error',
                        message='Dates not found',
                        code=404
                    )
                return standardize_response(
                    status='success',
                    data=[date for date in dates],
                    message='Dates retrieved successfully',
                    code=200
                )
            # if both event_id and user_id are provided, return the dates for the user
            elif 'user_id' in request.args and 'event_id' in request.args:
                user_id = request.args.get('user_id')
                dates = Date.get_dates_by_user_id(user_id)
                if not date:
                    return standardize_response(
                        status='error',
                        message='Date not found',
                        code=404
                    )
                return standardize_response(
                    status='success',
                    data=[d.to_dict() for d in dates],
                    message='Date retrieved successfully',
                    code=200
                )
            else:
                return standardize_response(
                    status='error',
                    message='Invalid request',
                    code=400
                )
        except Exception as e:
            current_app.logger.exception(e)
            return standardize_response(
                status='error',
                message='An error occurred while retrieving the dates',
                code=500
            )