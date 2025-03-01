from datetime import datetime, date
from .app import db
from sqlalchemy import DATE, Column, Date, DateTime, Float, ForeignKey, Integer, String, TIMESTAMP, and_, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT, BOOLEAN
from sqlalchemy.orm import relationship


# Define the Event model
class Event(db.Model):
    __tablename__ = 'event'

    event_id = Column(INTEGER(10, unsigned=True), primary_key=True)
    event_name = Column(String(45), nullable=False)
    description = Column(String(255))
    date_created = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    max_date = Column(DATE)
    min_date = Column(DATE)
    lon = Column(Float)
    lat = Column(Float)
    uuid = Column(String(45))
    is_active = Column(BOOLEAN)

    users = relationship('User', backref='event')
    dates = relationship('Date', backref='event')
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'event_name': self.event_name,
            'description': self.description,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'max_date': self.max_date.isoformat() if self.date_created else None,
            'min_date': self.min_date.isoformat() if self.date_created else None,
            'lon': self.lon,
            'lat': self.lat,
            'uuid': self.uuid,
            'is_active': self.is_active
        }

    @classmethod
    def create(cls, event_name, description, max_date, min_date,
               uuid, lon=None, lat=None, is_active=True):
        try:
            event = Event(
                event_name=event_name,
                description=description,
                max_date=max_date,
                min_date=min_date,
                lon=lon,
                lat=lat,
                uuid=uuid,
                is_active=is_active
            )
            db.session.add(event)
            return event
        except Exception as e:
            raise e
        
    @classmethod
    def update_name(cls, event_id, event_name):
        try:
            event = Event.query.get(event_id)
            event.event_name = event_name
            db.session.commit()
            return event
        except Exception as e:
            raise e

    @classmethod
    def update_description(cls, event_id, description):
        try:
            event = Event.query.get(event_id)
            event.description = description
            db.session.commit()
            return event
        except Exception as e:
            raise e
        
    @classmethod
    def update_location(cls, event_id, lon, lat):
        try:
            event = Event.query.get(event_id)
            event.lon = lon
            event.lat = lat
            db.session.commit()
            return event
        except Exception as e:
            raise e
        
    @classmethod
    def deactivate(cls, event_id):
        try:
            event = Event.query.get(event_id)
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
    
class User(db.Model):
    __tablename__ = 'user'

    user_id = Column(INTEGER(10, unsigned=True), primary_key=True)
    event_id = Column(ForeignKey('event.event_id', ondelete='NO ACTION', onupdate='NO ACTION'), nullable=False, index=True)
    name = Column(String(45), nullable=False)
    phone = Column(String(64))
    lat = Column(Float)
    lon = Column(Float)
    icon_path = Column(String(45))
    color = Column(String(45))
    is_driver = Column(BOOLEAN)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'event_id': self.event_id,
            'name': self.name,
            'phone': self.phone,
            'lat': self.lat,
            'lon': self.lon,
            'icon_path': self.icon_path,
            'color': self.color,
            'is_driver': self.is_driver
        }
    
    @classmethod
    def create(cls, event_id, name, phone, lat, lon, icon_path, color, is_driver):
        try:
            user = User(
                event_id=event_id,
                name=name,
                phone=phone,
                lat=lat,
                lon=lon,
                icon_path=icon_path,
                color=color,
                is_driver=is_driver
            )
            db.session.add(user)
            return user
        except Exception as e:
            raise e
        
    @classmethod
    def update_location(cls, user_id, lat, lon):
        try:
            user = User.query.get(user_id)
            user.lat = lat
            user.lon = lon
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
    is_blocked = Column(BOOLEAN)

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
