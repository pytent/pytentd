"""Tentd post types"""

from datetime import datetime

from sqlalchemy import (
    Table, Column, DateTime, ForeignKey, Integer, String, UnicodeText)

from tentd.models import db
from tentd.models.entity import Entity
from tentd.utils.types import JSONDict

class Post(db.Model):
    """A post belonging to an entity.
    
    Posts are at the core of Tent. Posts are sent to followers immediately after
    being created. The tent specifcation defines that there are two ways of
    accessing posts:

    `GET posts/` returns all posts, the parameters of the request define any
    filtering. There may need to be extra filtering for server-side performance.

    `GET posts/<id>` returns a post with the defined id.
    
    This is documented at: https://tent.io/docs/post-types
    """
    
    #: The column used to identify the objects type
    model_type = Column(String(50))
    
    __mapper_args__ = {
        'polymorphic_on': model_type,
    }

    id = Column(Integer, primary_key=True)
    
    entity_id = Column(Integer, ForeignKey('entity.id'))
    entity = db.relationship(
        'Entity', primaryjoin=entity_id==Entity.id, backref='posts')
    
    #: The time the post was published
    published_at = Column(DateTime)
    
    #: The time we received the post from the publishing server
    received_at = Column(DateTime)
    
    def __init__ (self, *args, **kwargs):
        """Creates a Post
    
        Automatically sets `published_at` and `received_at` to the current time
        if they are equal to `'now'`.
        """
        for time in ('published_at', 'received_at'):
            if kwargs.get(time, None) == 'now':
                kwargs[time] = datetime.utcnow()

        super(Post, self).__init__(*args, **kwargs)
    
    @property
    def schema (self):
        raise NotImplementedError("Schema not defined for this Post model")
    
    def content_to_json (self):
        raise NotImplementedError("Post model has not implemented content_to_json()")

    def to_json (self):
        """Returns the json for the post
    
        TODO: 'mentions'
        TODO: 'licenses'
        TODO: 'attachments'
        TODO: 'app'
        TODO: 'views'
        TODO: 'permissions'
        """
        json = {
            'id': self.id,
            'type': self.schema,
            'content': self.content_to_json(),
        }
        if self.entity:
            json['entity'] = self.entity.core.identifier
        if self.published_at:
            json['published_at'] = self.published_at.strftime("%s")
        if self.received_at:
            json['received_at'] = self.received_at.strftime("%s")
        return json
        
class GenericPost(Post):
    """A generic post type, for use when a post is unsupported by pytentd"""
    
    __mapper_args__ = {'polymorphic_identity': 'generic'}

    id = Column(Integer, ForeignKey('post.id'), primary_key=True)

    schema = Column(String(256), nullable=False)
    
    content = Column(JSONDict)

    def content_to_json(self):
        return self.content

class Status(Post):
    """The Status post type
    
    Contains either text, a location, or both.
    
    TODO: Locations are currently unsupported
    
    This is documented at: https://tent.io/docs/post-types#status
    """
    
    __mapper_args__ = {'polymorphic_identity': 'status'}

    id = Column(Integer, ForeignKey('post.id'), primary_key=True)
    
    schema = "https://tent.io/types/post/status/v0.1.0"

    text = Column(String(256))
    
    def content_to_json(self):
        return {'text': self.text}

class Essay(Post):
    """The Essay post type

    TODO: Support tags and excerpts
    """

    __mapper_args__ = {'polymorphic_identity': 'essay'}

    id = Column(Integer, ForeignKey('post.id'), primary_key=True)

    schema = "https://tent.io/types/post/essay/v0.1.0"

    title = Column(String)

    body = Column(UnicodeText)
    excerpt = Column(UnicodeText)
    
    def content_to_json(self):
        return {
            'title': self.title,
            'body': self.body
        }

class Repost(Post):
    """The Repost post type"""
    
    __mapper_args__ = {'polymorphic_identity': 'repost'}

    # id = Column(Integer, ForeignKey('post.id'), primary_key=True)

    schema = "https://tent.io/types/post/repost/v0.1.0"

    original_entity_id = Column(Integer, ForeignKey('entity.id'))
    original_entity = db.relationship(
        'Entity', primaryjoin=original_entity_id==Entity.id,
        doc="The entity that a post is being reposted from")

    original_post_id = Column(Integer, ForeignKey('post.id'))
    original_post = db.relationship(
        'Post', join_depth=1, remote_side=[Post.id],
        doc="The post that is being reposted")
    
    def content_to_json (self):
        return {
            'entity': self.entity.core.identifier,
            'id': self.original_post.id,
        }
