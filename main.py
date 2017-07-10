
from google.appengine.ext import ndb
import webapp2
import json

class boat(ndb.Model):
	name = ndb.StringProperty(required=True)
	type = ndb.StringProperty(required=True)
	length = ndb.IntegerProperty(required=True)
	at_sea = ndb.BooleanProperty()


class boatHandler(webapp2.RequestHandler):
	def post(self):
		boat_data = json.loads(self.request.body)
		new_boat = boat(name=boat_data['name'], type=boat_data['type'],
						length=boat_data['length'], at_sea=True)
		new_boat.put()
		boat_dict = new_boat.to_dict()
		boat_dict['kind'] = new_boat.key.kind()
		boat_dict['self'] = '/boats/' + new_boat.key.urlsafe()

		self.response.write(json.dumps(boat_dict))

	def get(self, id=None):
		if id:
			boat_data = ndb.Key(urlsafe=id).get()
			boat_dict = boat_data.to_dict()
			boat_dict['kind'] = ndb.Key(urlsafe=id).kind()
			boat_dict['self'] = "/boats/" + id

			self.response.write(json.dumps(boat_dict))


	def patch(self, id=None):
		if id:
			modify_data = json.loads(self.request.body)
			boat_entity = ndb.Key(urlsafe=id).get()

			if 'name' in modify_data:
				boat_entity.name = modify_data['name']
			if 'type' in modify_data:
				boat_entity.type = modify_data['type']
			if 'length' in modify_data:
				boat_entity.length = modify_data['length']

			boat_entity.put()

			boat_dict = boat_entity.to_dict()
			boat_dict['kind'] = ndb.Key(urlsafe=id).kind()
			boat_dict['self'] = "/boats/" + id

			self.response.write(json.dumps(boat_dict))


	def put(self, id=None):
		if id:
			replace_data = json.loads(self.request.body)
			boat_entity = ndb.Key(urlsafe=id).get()

			boat_entity.name = replace_data['name']
			boat_entity.type = replace_data['type']
			boat_entity.length = replace_data['length']

			boat_entity.put()

			boat_dict = boat_entity.to_dict()
			boat_dict['kind'] = ndb.Key(urlsafe=id).kind()
			boat_dict['self'] = "/boats/" + id

			self.response.write(json.dumps(boat_dict))


	def delete(self, id=None):
		if id:
			ndb.Key(urlsafe=id).delete()





class MainPage(webapp2.RequestHandler):

	def get(self):
		self.response.write("hello")



allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boats', boatHandler),
    ('/boats/(.*)', boatHandler),
], debug=True)
