""" Url converters """

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from werkzeug.routing import BaseConverter, ValidationError

class ModelConverter (BaseConverter):
	"""	Converts an url value to a model instance, and vice versa """
	
	app = model = field = None
	
	def to_python(self, value):
		with self.app.app_context():
			try:
				return self.model.query.filter_by(**{self.field: value}).one()
			except (MultipleResultsFound, NoResultFound):
				raise ValidationError()

	def to_url(self, value):
		return getattr(value, self.field)
		
	@classmethod
	def new (cls, app, model, field):
		"""	Returns a new ModelConverter type """
		name = model.__name__  + 'Converter'
		attrs = {'app': app, 'model': model, 'field': field}
		return type(name, (ModelConverter,), attrs)
