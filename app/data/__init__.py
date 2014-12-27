from flask_sqlalchemy import SQLAlchemy

mydb = SQLAlchemy()


import inspect
from functools import wraps, partial

def mapper(f=None,only=[], exclude=[], include_relations=True):
	if f is None:
		return partial(mapper, only=only, exclude=exclude, include_relations=include_relations)
	@wraps(f)
	def _wrap(*args, **kwargs):
		return as_dict(*args, only=only, exclude=exclude, include_relations=include_relations)
	return _wrap

def as_dict(obj, only=[], exclude=[], include_relations=True):
	hiddens = ["query_class", "query", "metadata"]
	pr = {}
	for name in dir(obj):
		value = getattr(obj, name)
		if isinstance(value, mydb.Model):
			if include_relations and not name in exclude:
				#re.match('('+name+').(.*)', 'hola.saludo.x.id').groups()
				pr[name] = value.toDict()
		elif only and name in only or not only and not name.startswith('_') and not name.startswith('__') and not inspect.ismethod(value) and not name in hiddens and not name in exclude :
			pr[name] = value
	return pr


class DictMapper():
	@mapper
	def toDict(self):
		pass

	def toCustomDict(self, only=[], exclude=[], include_relations=True):
		return as_dict(obj, only=only, exclude=exclude, include_relations=include_relations)
		
	def fromDict(self, dictionary):
		pass

