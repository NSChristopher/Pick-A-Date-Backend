from datetime import datetime
import random
from flask import Flask, jsonify, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields
from .utilities import Utility
from .configs import DevelopmentConfig, TestingConfig, ProductionConfig

import os
import uuid
import logging

standardize_response = Utility.standardize_response

# Initialize extensions outside
db = SQLAlchemy()
api = Api()

def create_app(config_name=None):
    app = Flask(__name__)

    config_modes = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }

    config_mode = config_modes.get(config_name, DevelopmentConfig)
    app.config.from_object(config_mode)

    # Initialize extensions after configuring the app
    db.init_app(app)
    api.init_app(app)

    logging.basicConfig(level=logging.DEBUG)

    with app.app_context():
        # Import models here
        from .models import Date, Event, User, Address, EntityTypeEnum
        db.create_all()


        address_model = api.model('Address', {
            'address_id': fields.Integer,
            'address_name': fields.String,
            'street_line_1': fields.String,
            'street_line_2': fields.String,
            'city': fields.String,
            'state_or_province': fields.String,
            'country_code': fields.String,
            'postal_code': fields.String,
        })

        event_model = api.model('Event', {
            'event_id': fields.Integer,
            'event_name': fields.String,
            'description': fields.String,
            'date_created': fields.DateTime,
            'min_date': fields.Date,
            'max_date': fields.Date,
            'uuid': fields.String,
            'is_active': fields.Boolean,
            'addresses': fields.List(fields.Nested(address_model), required=False)
        })

        events_ns = api.namespace('events', description='Events related operations')
        api.add_namespace(events_ns)

        @events_ns.route('/event')
        class event(Resource):
            @events_ns.expect(event_model)
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
                        uuid=str(uuid.uuid4())
                    )
                    db.session.flush()
                    
                    addresses_data = data.get('addresses', [])
                    if len(addresses_data) > 0:
                        for address in addresses_data:
                            address = Address.create(
                                entity_type=EntityTypeEnum.EVENT,
                                entity_id=event.event_id,
                                address_name=address.get('address_name', ''),
                                street_line_1=address.get('street_line_1', ''),
                                street_line_2=address.get('street_line_2', ''),
                                city=address.get('city', ''),
                                state_or_province=address.get('state_or_province', ''),
                                country_code=address.get('country_code', ''),
                                postal_code=address.get('postal_code', ''),
                                latitude=address.get('lat', None),
                                longitude=address.get('lon', None)
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
                    
                    addresses = Address.get_addresses_by_entity_id(entity_type=EntityTypeEnum.EVENT, entity_id=event.event_id)
                    event_data = event.to_dict()
                    event_data['addresses'] = [addres.to_dict() for addres in addresses] if addresses else []


                    return standardize_response(
                        status='success',
                        data=event_data,
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
            'postal_code': fields.String,
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
                        postal_code=data['postal_code'],
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
                
        return app