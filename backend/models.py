from datetime import datetime, date
import enum
from .app import db
from sqlalchemy import Column, Date, DateTime, String, Enum, ForeignKey, Numeric, Index, UniqueConstraint, CheckConstraint, and_, text, Integer
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, BOOLEAN
from sqlalchemy.orm import relationship
import uuid
import secrets

def generate_uuid():
    return str(uuid.uuid4())

def generate_token(length=32):
    return secrets.token_urlsafe(length)

class Event(db.Model):
    __tablename__ = 'event'

    event_uuid = Column(String(45), primary_key=True, default=generate_uuid)
    event_name = Column(String(45), nullable=False)
    description = Column(String(255))
    date_created = Column(DateTime, nullable=False, server_default=db.func.current_timestamp())
    # default max_date to 30 days from today and min_date to 1 day from today
    max_date = Column(Date, nullable=False, default=lambda: date.today() + timedelta(days=30)) 
    min_date = Column(Date, nullable=False, default=lambda: date.today() + timedelta(days=1))
    is_active = Column(BOOLEAN, default=True, nullable=False)

    participants = relationship('Participant', backref='event', cascade="all, delete")
    dates = relationship('Date', backref='event', cascade="all, delete")
    access_tokens = relationship('AccessToken', backref='event', cascade="all, delete")
    addresses = relationship('EventAddress', backref='event', cascade="all, delete")

    def to_dict(self):
        return {
            'event_name': self.event_name,
            'description': self.description,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'max_date': self.max_date.isoformat() if self.max_date else None,
            'min_date': self.min_date.isoformat() if self.min_date else None,
            'is_active': self.is_active,
            'addresses': [
                {
                    'event_address_id': a.event_address_id,
                    'address_name': a.address_name,
                    'street_line_1': a.street_line_1,
                    'street_line_2': a.street_line_2,
                    'city': a.city,
                    'state_or_province': a.state_or_province,
                    'country_code': a.country_code,
                    'postal_code': a.postal_code,
                    'latitude': float(a.latitude) if a.latitude is not None else None,
                    'longitude': float(a.longitude) if a.longitude is not None else None
                } for a in self.addresses
            ]
        }

    def to_detail_dict(self):
        return {
            'event_name': self.event_name,
            'description': self.description,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'max_date': self.max_date.isoformat() if self.max_date else None,
            'min_date': self.min_date.isoformat() if self.min_date else None,
            'is_active': self.is_active,
            'participants_count': len(self.participants),
            'addresses_count': len(self.addresses),
            'participants': [
                {
                    'participant_id': p.participant_id,
                    'name': p.name,
                    'phone': p.phone,
                    'postal_code': p.postal_code,
                    'icon_path': p.icon_path,
                    'color': p.color,
                    'is_driver': p.is_driver,
                    'role': p.role
                } for p in self.participants
            ],
            'addresses': [
                {
                    'event_address_id': a.event_address_id,
                    'address_name': a.address_name,
                    'street_line_1': a.street_line_1,
                    'street_line_2': a.street_line_2,
                    'city': a.city,
                    'state_or_province': a.state_or_province,
                    'country_code': a.country_code,
                    'postal_code': a.postal_code,
                    'latitude': float(a.latitude) if a.latitude is not None else None,
                    'longitude': float(a.longitude) if a.longitude is not None else None
                } for a in self.addresses
            ],
            'dates': [
                {
                    'date_id': d.date_id,
                    'participant_id': d.participant_id,
                    'date': d.date.isoformat() if d.date else None,
                    'availability_level': d.availability_level
                } for d in self.dates
            ]
        }

    @classmethod
    def create(cls, event_name, description, max_date, min_date, is_active=True):
        try:
            event = Event(
                event_name=event_name,
                description=description,
                max_date=max_date,
                min_date=min_date,
                is_active=is_active
            )
            db.session.add(event)
            return event
        except Exception as e:
            raise e

    @classmethod
    def update_name(cls, event_uuid, event_name):
        try:
            event = Event.query.get(event_uuid)
            event.event_name = event_name
            db.session.commit()
            return event
        except Exception as e:
            raise e

    @classmethod
    def update_description(cls, event_uuid, description):
        try:
            event = Event.query.get(event_uuid)
            event.description = description
            db.session.commit()
            return event
        except Exception as e:
            raise e

    @classmethod
    def deactivate(cls, event_uuid):
        try:
            event = Event.query.get(event_uuid)
            event.is_active = False
            db.session.commit()
            return event
        except Exception as e:
            raise e

    @classmethod
    def get_event_by_uuid(cls, uuid):
        try:
            return Event.query.filter_by(event_uuid=uuid).first()
        except Exception as e:
            raise e

class Account(db.Model):
    __tablename__ = 'account'
    __table_args__ = (UniqueConstraint('email', name='uix_email'),)

    account_id = Column(String(45), primary_key=True, default=generate_uuid)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(64))
    postal_code = Column(String(20))
    icon_path = Column(String(255))
    color = Column(String(45))
    is_active = Column(BOOLEAN, default=True)
    created_at = Column(DateTime, default=db.func.current_timestamp())
    updated_at = Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def to_dict(self):
        return {
            'account_id': self.account_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'postal_code': self.postal_code,
            'icon_path': self.icon_path,
            'color': self.color,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Participant(db.Model):
    __tablename__ = 'participant'
    __table_args__ = (UniqueConstraint('event_uuid', 'phone', name='uix_event_account_phone'),)

    participant_id = Column(INTEGER(unsigned=True), primary_key=True)
    event_uuid = Column(String(45), ForeignKey('event.event_uuid'), nullable=False)
    account_id = Column(String(45), ForeignKey('account.account_id'), nullable=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(64))
    postal_code = Column(String(20))
    icon_path = Column(String(255))
    color = Column(String(45))
    is_driver = Column(BOOLEAN, default=False)
    role = Column(Enum('organizer', 'participant'), nullable=False, default='participant')

    dates = relationship('Date', backref='participant', cascade="all, delete")

    def to_dict(self):
        return {
            'participant_id': self.participant_id,
            'account_id': self.account_id,
            'name': self.name,
            'phone': self.phone,
            'postal_code': self.postal_code,
            'icon_path': self.icon_path,
            'color': self.color,
            'is_driver': self.is_driver,
            'role': self.role
        }

    def to_detail_dict(self):
        return {
            'participant_id': self.participant_id,
            'name': self.name,
            'phone': self.phone,
            'postal_code': self.postal_code,
            'icon_path': self.icon_path,
            'color': self.color,
            'is_driver': self.is_driver,
            'role': self.role,
            'selected_dates': [
                {
                    'date_id': date.date_id,
                    'date': date.date.isoformat() if date.date else None,
                    'availability_level': date.availability_level
                } for date in self.dates
            ]
        }

    @classmethod
    def create(cls, event_uuid, name, phone, postal_code, icon_path, color, is_driver):
        try:
            participant = Participant(
                event_uuid=event_uuid,
                name=name,
                phone=phone,
                postal_code=postal_code,
                icon_path=icon_path,
                color=color,
                is_driver=is_driver
            )
            db.session.add(participant)
            return participant
        except Exception as e:
            raise e

    @classmethod
    def update_location(cls, participant_id, postal_code):
        try:
            participant = Participant.query.get(participant_id)
            participant.postal_code = postal_code
            db.session.commit()
            return participant
        except Exception as e:
            raise e

    @classmethod
    def update_is_driver(cls, participant_id, is_driver):
        try:
            participant = Participant.query.get(participant_id)
            participant.is_driver = is_driver
            db.session.commit()
            return participant
        except Exception as e:
            raise e

    @classmethod
    def get_participants_by_event_uuid(cls, event_uuid):
        try:
            return Participant.query.filter_by(event_uuid=event_uuid).all()
        except Exception as e:
            raise e

    @classmethod
    def get_participant_by_phone_and_event_uuid(cls, phone, event_uuid):
        try:
            return Participant.query.filter_by(phone=phone, event_uuid=event_uuid).first()

        except Exception as e:
            raise e

    @classmethod
    def get_participants_by_date(cls, date: date | str):
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, "%Y-%m-%d").date()
            return Participant.query.join(Date, Participant.participant_id == Date.participant_id).filter(
                and_(Date.date == date, Date.availability_level != 2)  # 2: Unavailable
            ).all()
        except Exception as e:
            raise e

class Date(db.Model):
    __tablename__ = 'date'
    __table_args__ = (
        UniqueConstraint('event_uuid', 'participant_id', 'date', name='uix_participant_date'),
        CheckConstraint('availability_level IN (0, 1, 2)', name='check_availability_level')
    )

    date_id = Column(INTEGER(unsigned=True), primary_key=True)
    event_uuid = Column(String(45), ForeignKey('event.event_uuid'), nullable=False, index=True)
    participant_id = Column(INTEGER(unsigned=True), ForeignKey('participant.participant_id'), nullable=False, index=True)
    date = Column(Date, nullable=False)
    availability_level = Column(Integer, nullable=False, default=0)  # 0: Available, 1: Tentative, 2: Unavailable

    def to_dict(self):
        return {
            'date_id': self.date_id,
            'participant_id': self.participant_id,
            'date': self.date.isoformat() if self.date else None,
            'availability_level': self.availability_level
        }

    @classmethod
    def get_date_by_date_by_id_participant_and_event(cls, date_id, participant_id, event_uuid):
        try:
            return Date.query.filter_by(date_id=date_id, participant_id=participant_id, event_uuid=event_uuid).first()
        except Exception as e:
            raise e

    @classmethod
    def get_dates_by_participant_and_event(cls, participant_id, event_uuid):
        try:
            return Date.query.filter_by(participant_id=participant_id, event_uuid=event_uuid).all()
        except Exception as e:
            raise e

    @classmethod
    def create(cls, event_uuid, participant_id, date, availability_level=0):
        try:
            d = Date(
                event_uuid=event_uuid,
                participant_id=participant_id,
                date=date,
                availability_level=availability_level
            )
            db.session.add(d)
            return d
        except Exception as e:
            raise e

class EventAddress(db.Model):
    __tablename__ = 'event_address'

    event_address_id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    event_uuid = Column(String(45), ForeignKey('event.event_uuid'), nullable=False)
    address_name = Column(String(255), nullable=False)
    street_line_1 = Column(String(255), nullable=False)
    street_line_2 = Column(String(255))
    city = Column(String(255), nullable=False)
    state_or_province = Column(String(255), nullable=False)
    country_code = Column(String(2), nullable=False)
    postal_code = Column(String(20), nullable=False)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))

    def to_dict(self):
        return {
            'event_address_id': self.event_address_id,
            'address_name': self.address_name,
            'street_line_1': self.street_line_1,
            'street_line_2': self.street_line_2,
            'city': self.city,
            'state_or_province': self.state_or_province,
            'country_code': self.country_code,
            'postal_code': self.postal_code,
            'latitude': float(self.latitude) if self.latitude is not None else None,
            'longitude': float(self.longitude) if self.longitude is not None else None
        }

    @classmethod
    def create(cls, event_uuid, address_name, street_line_1, street_line_2, city, state_or_province, country_code, postal_code, latitude=None, longitude=None):
        try:
            address = EventAddress(
                event_uuid=event_uuid,
                address_name=address_name,
                street_line_1=street_line_1,
                street_line_2=street_line_2,
                city=city,
                state_or_province=state_or_province,
                country_code=country_code,
                postal_code=postal_code,
                latitude=latitude,
                longitude=longitude
            )
            db.session.add(address)
            return address
        except Exception as e:
            raise e

class AccessToken(db.Model):
    __tablename__ = 'access_token'

    token = Column(String(64), primary_key=True)
    event_uuid = Column(String(45), ForeignKey('event.event_uuid'), nullable=False, index=True)
    account_id = Column(String(45), nullable=False, index=True)
    created_at = Column(DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'token': self.token,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def create(cls, event_uuid, account_id=None):
        try:
            token = AccessToken(
                token=generate_token(),
                event_uuid=event_uuid,
                account_id=0 if account_id is None else account_id,
            )
            db.session.add(token)
            return token
        except Exception as e:
            raise e
    @classmethod
    def get_by_token(cls, token):
        try:
            return AccessToken.query.filter_by(token=token).first()
        except Exception as e:
            raise e
