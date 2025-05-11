from datetime import datetime
import random
from flask import Flask, jsonify, request, current_app, g
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields
from .utilities import Utility
from .configs import DevelopmentConfig, TestingConfig, ProductionConfig
from .services.token_decorator import token_required

import os
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
        from .models import Date, Event, Account, Participant, Date, EventAddress, AccessToken
        db.create_all()


        participant_list_model = api.model('ParticipantDetail', {
            'participant_id': fields.Integer,
            'name': fields.String,
            'phone': fields.String,
            'postal_code': fields.String,
            'icon_path': fields.String,
            'color': fields.String,
            'is_driver': fields.Boolean
        })

        event_address_model = api.model('Address', {
            'event_address_id': fields.Integer,
            'address_name': fields.String,
            'street_line_1': fields.String,
            'street_line_2': fields.String,
            'city': fields.String,
            'state_or_province': fields.String,
            'country_code': fields.String,
            'postal_code': fields.String,
            'latitude': fields.Float,
            'longitude': fields.Float
        })

        date_list_model = api.model('DateCreate', {
            'date_id': fields.Integer,
            'participant_id': fields.Integer,
            'date': fields.DateTime,
            'availability_level': fields.Integer  # 0: available, 1: preferred, 2: unavailable
        })

        event_detail_model = api.model('EventDetail', {
            'event_uuid': fields.String,
            'event_name': fields.String,
            'description': fields.String,
            'date_created': fields.DateTime,
            'max_date': fields.Date,
            'min_date': fields.Date,
            'is_active': fields.Boolean,
            'participants_count': fields.Integer,
            'addresses_count': fields.Integer,
            'participants': fields.List(fields.Nested(participant_list_model), required=False),
            'addresses': fields.List(fields.Nested(event_address_model), required=False),
            'dates': fields.List(fields.Nested(date_list_model), required=False)
        })

        event_address_create_model = api.model('AddressCreate', {
            'address_name': fields.String,
            'street_line_1': fields.String,
            'street_line_2': fields.String,
            'city': fields.String,
            'state_or_province': fields.String,
            'country_code': fields.String(default='US'),
            'postal_code': fields.String,
            'latitude': fields.Float,
            'longitude': fields.Float
        })

        event_create_model = api.model('EventCreate', {
            'event_name': fields.String,
            'description': fields.String,
            'max_date': fields.Date,
            'min_date': fields.Date,
            'addresses': fields.List(fields.Nested(event_address_create_model), required=False)
        })

        events_ns = api.namespace('events', path='/events', description='Event operations')
        api.add_namespace(events_ns)

        @events_ns.route('')
        class EventListResource(Resource):
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
                        min_date=min_date
                    )
                    db.session.flush()
                    
                    addresses_data = data.get('addresses', [])
                    if len(addresses_data) > 0:
                        for address in addresses_data:
                            address = EventAddress.create(
                                event_uuid=event.event_uuid,
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

                    token = AccessToken.create(
                        event_uuid=event.event_uuid
                    )

                    db.session.commit()
                    return standardize_response(
                        status='success',
                        data=token.to_dict(),
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


        @events_ns.route('/<string:token>')
        class EventDetailResource(Resource):
            @token_required()
            def get(self, token):
                try:
                    event_uuid = g.event_uuid
                    event = Event.get_event_by_uuid(event_uuid)
                    if not event:
                        return standardize_response(
                            status='error',
                            message='Event not found',
                            code=404
                        )
                    return standardize_response(
                        status='success',
                        data=event.to_detail_dict(),
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

        participant_create_model = api.model('ParticipantCreate', {
            'name': fields.String,
            'phone': fields.String,
            'postal_code': fields.String,
            'is_driver': fields.Boolean
        })

        participants_ns = api.namespace('participants', path='/events/<string:token>/participants', description='Participant operations')
        api.add_namespace(participants_ns)

        @participants_ns.route('')
        class ParticipantListResource(Resource):
            @token_required()
            @participants_ns.expect(participant_create_model)
            def post(self, token):
                try:
                    event_uuid = g.event_uuid
                    data = request.get_json()
                    participant = Participant.create(
                        event_uuid=event_uuid,
                        name=data['name'],
                        phone=data['phone'],
                        postal_code=data['postal_code'],
                        icon_path='default.png',
                        color='#' + '%06x' % random.randint(0, 0xFFFFFF),
                        is_driver=data['is_driver']
                    )
                    db.session.commit()
                    return standardize_response(
                        status='success',
                        data=participant.to_dict(),
                        message='Participant created successfully',
                        code=201
                    )
                except Exception as e:
                    current_app.logger.exception(e)
                    return standardize_response(
                        status='error',
                        message='An error occurred while creating the participant',
                        code=500
                    )
            @token_required()
            def get(self, token):
                try:
                    event_uuid = g.event_uuid
                    participants = Participant.get_participants_by_event_uuid(event_uuid) # TODO Fix this line, it should be token not event_uuid
                    return standardize_response(
                        status='success',
                        data={'participants': [p.to_dict() for p in participants]},
                        message='Participants retrieved successfully',
                        code=200
                    )
                except Exception as e:
                    current_app.logger.exception(e)
                    return standardize_response(
                        status='error',
                        message='An error occurred while retrieving the participants',
                        code=500
                    )

        participant_detail_model = api.model('ParticipantDetail', {
            'participant_id': fields.Integer,
            'name': fields.String,
            'phone': fields.String,
            'postal_code': fields.String,
            'icon_path': fields.String,
            'color': fields.String,
            'is_driver': fields.Boolean,
            'role': fields.String,
            'selected_dates': fields.List(fields.Nested(date_list_model), required=False)
        })
                

        @participants_ns.route('/<string:phone>')
        class ParticipantDetailResource(Resource):
            @token_required()
            def get(self, phone, token):
                try:
                    event_uuid = g.event_uuid
                    participant = Participant.get_participant_by_phone_and_event_uuid(phone=phone, event_uuid=event_uuid)
                    if not participant:
                        return standardize_response(status='error', message='Participant not found', code=404)
                    return standardize_response(status='success', data=participant.to_dict(), message='Participant retrieved successfully', code=200)

                except Exception as e:
                    current_app.logger.exception(e)
                    return standardize_response(status='error', message='Failed to retrieve participants', code=500)      
            
        date_create_model = api.model('DateCreate', {
            'date': fields.DateTime(default='2023-10-01'),
            'availability_level': fields.Integer  # 0: available, 1: preferred, 2: unavailable
        })

        dates_ns = api.namespace('dates', path='/events/<string:token>/participants/<string:participant_id>/dates', description='Date operations')
        api.add_namespace(dates_ns)
        
        @dates_ns.route('')
        class DateListResource(Resource):
            @token_required()
            @dates_ns.expect(date_create_model)
            def post(self, participant_id, token):
                try:
                    event_uuid = g.event_uuid
                    data = request.get_json()
                    d = datetime.strptime(data['date'], '%Y-%m-%d').date()
                    date = Date.create(
                        event_uuid=event_uuid,
                        participant_id=participant_id,
                        date=d,
                        availability_level=data['availability_level']
                    )
                    db.session.commit()
                    return standardize_response(status='success', data=date.to_dict(), message='Date created', code=201)
                except Exception as e:
                    current_app.logger.exception(e)
                    return standardize_response(status='error', message='Failed to create date', code=500)

            @token_required()
            def get(self, participant_id, token):
                try:
                    event_uuid = g.event_uuid
                    dates = Date.get_dates_by_participant_and_event(event_uuid=event_uuid, participant_id=participant_id)
                    return standardize_response(status='success', data=[d.to_dict() for d in dates], message='Dates retrieved', code=200)
                except Exception as e:
                    current_app.logger.exception(e)
                    return standardize_response(status='error', message='Failed to retrieve dates', code=500)

        @dates_ns.route('/<int:date_id>')
        class DateDetailResource(Resource):
            @token_required()
            def delete(self, participant_id, date_id, token):
                try:
                    event_uuid = g.event_uuid
                    date = Date.get_date_by_date_by_id_participant_and_event(participant_id=participant_id, event_uuid=event_uuid, date_id=date_id)
                    if not date:
                        return standardize_response(status='error', message='Date not found', code=404)
                    db.session.delete(date)
                    db.session.commit()
                    return standardize_response(status='success', message='Date deleted successfully', code=200)
                except Exception as e:
                    current_app.logger.exception(e)
                    return standardize_response(status='error', message='Failed to delete date', code=500)
                
            @token_required()
            @dates_ns.expect(date_create_model)
            def put(self, participant_id, date_id, token):
                try:
                    event_uuid = g.event_uuid
                    
                    data = request.get_json()
                    d = datetime.strptime(data['date'], '%Y-%m-%d').date()
                    availability_level = data['availability_level']
                    if d is None or availability_level is None:
                        return standardize_response(status='error', message='Invalid request', code=400)

                    date = Date.get_date_by_date_by_id_participant_and_event(participant_id=participant_id, event_uuid=event_uuid, date_id=date_id)
                    if not date:
                        return standardize_response(status='error', message='Date not found', code=404)
                    
                    date.date = d
                    date.availability_level = availability_level
                    db.session.commit()
                    return standardize_response(status='success', data=date.to_dict(), message='Date updated successfully', code=200)

                except Exception as e:
                    current_app.logger.exception(e)
                    return standardize_response(status='error', message='Failed to update date', code=500)
        return app