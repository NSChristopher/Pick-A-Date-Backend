from datetime import datetime, date
import enum
from .app import db
from sqlalchemy import DATE, Column, Date, DateTime, Float, ForeignKey, Integer, String, TIMESTAMP, and_, text, Enum, Numeric, Index
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, BOOLEAN
from sqlalchemy.orm import relationship
import uuid

# Abstract uuid class for generating UUIDs for easy future switching
def generate_uuid():
    return str(uuid.uuid4())


# Define the Event model
class Event(db.Model):
    __tablename__ = 'event'

    event_uuid = Column(String(45), primary_key=True, default=generate_uuid)
    event_name = Column(String(45), nullable=False)
    description = Column(String(255))
    date_created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    max_date = Column(DATE)
    min_date = Column(DATE)
    is_active = Column(BOOLEAN)

    users = relationship('User', backref='event')
    dates = relationship('Date', backref='event')
    
    def to_dict(self):
        return {
            'event_uuid': self.event_uuid,
            'event_name': self.event_name,
            'description': self.description,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'max_date': self.max_date.isoformat() if self.date_created else None,
            'min_date': self.min_date.isoformat() if self.date_created else None,
            'is_active': self.is_active
        }

    @classmethod
    def create(cls, event_name, description, max_date, min_date,
               uuid, is_active=True):
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
            return Event.query.filter_by(uuid=uuid).first()
        except Exception as e:
            raise e

class EntityTypeEnum(enum.Enum):
    EVENT = "event"
    USER = "user"

class Address(db.Model):
    __tablename__ = 'address'
    __table_args__ = (
        Index('entity_id_idx', 'entity_type', 'entity_id'),
    )

    address_id = Column(INTEGER(10, unsigned=True), primary_key=True)
    entity_type = Column(Enum(EntityTypeEnum), nullable=False)
    entity_id = Column(INTEGER(10, unsigned=True), nullable=False)
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
            "address_id": self.address_id,
            "entity_type": self.entity_type.value,
            "entity_id": self.entity_id,
            "address_name": self.address_name,
            "street_line_1": self.street_line_1,
            "street_line_2": self.street_line_2,
            "city": self.city,
            "state_or_province": self.state_or_province,
            "country_code": self.country_code,
            "postal_code": self.postal_code,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
        }
    
    @classmethod
    def create(cls, entity_type, entity_id, address_name, street_line_1, street_line_2,
               city, state_or_province, country_code, postal_code, latitude=None, longitude=None):
        try:
            address = Address(
                entity_type=entity_type,
                entity_id=entity_id,
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
        
    @classmethod
    def get_addresses_by_entity_id(cls, entity_type, entity_id):
        try:
            return Address.query.filter_by(entity_type=entity_type, entity_id=entity_id).all()
        except Exception as e:
            raise e
    
class User(db.Model):
    __tablename__ = 'user'

    user_id = Column(INTEGER(10, unsigned=True), primary_key=True)
    event_id = Column(ForeignKey('event.event_id', ondelete='NO ACTION', onupdate='NO ACTION'), nullable=False, index=True)
    name = Column(String(45), nullable=False)
    phone = Column(String(64))
    postal_code = Column(String(20))
    icon_path = Column(String(45))
    color = Column(String(45))
    is_driver = Column(BOOLEAN)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'event_id': self.event_id,
            'name': self.name,
            'phone': self.phone,
            'postal_code': self.postal_code,
            'icon_path': self.icon_path,
            'color': self.color,
            'is_driver': self.is_driver
        }
    
    @classmethod
    def create(cls, event_id, name, phone, postal_code, icon_path, color, is_driver):
        try:
            user = User(
                event_id=event_id,
                name=name,
                phone=phone,
                postal_code=postal_code,
                icon_path=icon_path,
                color=color,
                is_driver=is_driver
            )
            db.session.add(user)
            return user
        except Exception as e:
            raise e
        
    @classmethod
    def update_location(cls, user_id, postal_code):
        try:
            user = User.query.get(user_id)
            user.postal_code = postal_code
            db.session.commit()
            return user
        except Exception as e:
            raise e        
        
    @classmethod
    def update_is_driver(cls, user_id, is_driver):
        try:
            user = User.query.get(user_id)
            user.is_driver = is_driver
            db.session.commit()
            return user
        except Exception as e:
            raise e
        
    @classmethod
    def get_users_by_event_id(cls, event_id):
        try:
            return User.query.filter_by(event_id=event_id).all()
        except Exception as e:
            raise e

    @classmethod
    def get_user_by_phone_and_event_id(cls, phone, event_id):
        try:
            return User.query.filter_by(phone=phone, event_id=event_id).first()
        except Exception as e:
            raise e
    
    # given a date (as a string in 'YYYY-MM-DD' format or as a datetime.date object),
    # return all users who have a date blocked out on that date
    @classmethod
    def get_users_by_date(cls, date: date | str):
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, "%Y-%m-%d").date()
            return User.query.join(Date, User.user_id == Date.user_id).filter(
                and_(Date.date == date, Date.is_blocked == False)
            ).all()
        except Exception as e:
            raise e


class Date(db.Model):
    __tablename__ = 'date'

    date_id = Column(INTEGER(10, unsigned=True), primary_key=True)
    event_id = Column(ForeignKey('event.event_id', ondelete='NO ACTION', onupdate='NO ACTION'), nullable=False, index=True)
    user_id = Column(ForeignKey('user.user_id', ondelete='NO ACTION', onupdate='NO ACTION'), nullable=False, index=True)
    date = Column(DATE, nullable=False)
    is_blocked = Column(BOOLEAN) # TODO: types of dates (blocked, available, ideal, etc.)

    def to_dict(self):
        return {
            'date_id': self.date_id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'is_blocked': self.is_blocked
        }
    
    # get dates by event id and include a list of users who have blocked out that date
    @classmethod
    def get_dates_by_event_id(cls, event_id):
        try:
            # Query for unique dates and related user info within the given event
            results = db.session.query(
                Date.date, 
                Date.is_blocked, 
                User.name, 
                User.color, 
                User.icon_path
            ).join(User, User.user_id == Date.user_id).filter(Date.event_id == event_id).all()

            date_dict = {}
            for date, is_blocked, user_name, user_color, user_icon_path in results:
                date_str = date.strftime("%Y-%m-%d")  # Format date as "YYYY-MM-DD"
                if date_str not in date_dict:
                    date_dict[date_str] = {
                        "is_blocked": is_blocked,
                        "users": []
                    }
                date_dict[date_str]["users"].append({
                    "name": user_name,
                    "color": user_color,
                    "icon_path": user_icon_path
                })

            date_list = [{"date": date, **details} for date, details in date_dict.items()]

            return date_list

        except Exception as e:
            raise e
        
    @classmethod
    def get_dates_by_user_id(cls, user_id):
        try:
            return Date.query.filter_by(user_id=user_id).all()
        except Exception as e:
            raise e
        
    @classmethod
    def create(cls, event_id, user_id, date, is_blocked=False):
        try:
            date = Date(
                event_id=event_id,
                user_id=user_id,
                date=date,
                is_blocked=is_blocked
            )
            db.session.add(date)
            return date
        except Exception as e:
            raise e
        
    @classmethod
    def delete(cls, date_id, user_id):
        try:
            date = Date.query.filter_by(date_id=date_id, user_id=user_id).first()
            db.session.delete(date)
            db.session.commit()
        except Exception as e:
            raise e
