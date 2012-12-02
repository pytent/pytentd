""" Url converters """

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from werkzeug.routing import BaseConverter, ValidationError

from tentd.models.entity import Entity

class ModelConverter (BaseConverter):
	def to_python(self, value):
		with self.app.app_context():
			return self.model.query.filter_by(**{self.field: value}).first_or_404()

	def to_url(self, value):
		return getattr(value, self.field)
		
	@classmethod
	def new (cls, app, model, field):
		name = model.__name__  + 'Converter'
		attrs = {'app': app, 'model': model, 'field': field}
		return type(name, (ModelConverter,), attrs)

class EntityCoverter (ModelConverter):
	@classmethod
	def new (cls, app):
		return super(EntityCoverter, cls).new(app, Entity, 'name')
