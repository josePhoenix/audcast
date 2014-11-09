from sqlalchemy import (Column, ForeignKey, Integer, String, Unicode, UnicodeText,
                        Boolean, DateTime)
from sqlalchemy.orm import relationship
import feedparser

from audcast.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), unique=True)
    pin = Column(Unicode(4), unique=True)

    def __init__(self, name, pin):
        self.name = name
        self.pin = pin

    def __repr__(self):
        return '<User: {0} [{1}]>'.format(self.name, self.pin)

class Feed(Base):
    __tablename__ = 'feeds'
    id = Column(Integer, primary_key=True)
    url = Column(Unicode(128), unique=True)
    name = Column(Unicode(128))
    last_refresh = Column(DateTime, nullable=True)
    last_refresh_new_count = Column(Integer, nullable=True)
    episodes = relationship("Episode", backref="feed")

    def __init__(self, url):
        self.url = url

    def update(self):
        feed_content = feedparser.parse(self.url)
        self.name = feed_content['feed']['title']

    def __repr__(self):
        return '<Feed: {0} [{1}]>'.format(self.name, self.url)

class Episode(Base):
    __tablename__ = 'episodes'
    id = Column(Integer, primary_key=True)
    feed_id = Column(Integer, ForeignKey('feeds.id'))
    name = Column(Unicode(128), unique=True)
    description = Column(UnicodeText)
    played = Column(Boolean, default=False)
    filename = Column(Unicode(128), unique=True)

    def __init__(self, feed, name, description, filename):
        self.feed = feed
        self.name = name
        self.description = description
        self.filename = filename

    def __repr__(self):
        return '<Episode: {0} [{1}]>'.format(self.name, self.feed.name)
