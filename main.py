
from google.appengine.ext import ndb
import webapp2
import json


class boat(ndb.Model):
	id = ndb.StringProperty()
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
		new_boat.id = str(new_boat.key.urlsafe())
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

			if 'at_sea' in modify_data:
				if modify_data['at_sea']:
					#remove a boat from a slip
					slip_with_boat_list = slip.query(slip.current_boat == id).fetch()
					slip_with_boat = slip_with_boat_list[0]
					slip_with_boat.current_boat = None
					slip_with_boat.arrival_date = None
					slip_with_boat.put()

					boat_entity.at_sea = False
				else:
					boat_entity.at_sea = True

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



class slip(ndb.Model):
	id = ndb.StringProperty()
	number = ndb.IntegerProperty(required=True)
	current_boat = ndb.StringProperty()
	arrival_date = ndb.StringProperty()



class slipHandler(webapp2.RequestHandler):

	def post(self):
		slip_data = json.loads(self.request.body)
		new_slip = slip(number=slip_data['number'])

		new_slip.put()
		new_slip.id = str(new_slip.key.urlsafe())
		new_slip.put()

		slip_dict = new_slip.to_dict()
		slip_dict['kind'] = new_slip.key.kind()
		slip_dict['self'] = '/slips/' + new_slip.key.urlsafe()

		self.response.write(json.dumps(slip_dict))


	def get(self, id=None):
		if id:
			slip_data = ndb.Key(urlsafe=id).get()
			slip_dict = slip_data.to_dict()
			slip_dict['kind'] = ndb.Key(urlsafe=id).kind()
			slip_dict['self'] = "/slips/" + id

			self.response.write(json.dumps(slip_dict))


	def patch(self, id=None):
		if id:
			modify_data = json.loads(self.request.body)
			slip_entity = ndb.Key(urlsafe=id).get()

			if 'number' in modify_data:
				slip_entity.number = modify_data['number']


			if 'arrival_date' in modify_data:
				slip_entity.arrival_date = modify_data['arrival_date']

			slip_entity.put()

			slip_dict = slip_entity.to_dict()
			slip_dict['kind'] = ndb.Key(urlsafe=id).kind()
			slip_dict['self'] = "/slips/" + id

			self.response.write(json.dumps(slip_dict))


	def put(self, id=None):
		if id:
			replace_data = json.loads(self.request.body)
			slip_entity = ndb.Key(urlsafe=id).get()

			slip_entity.number = replace_data['number']
			slip_entity.current_boat = replace_data['current_boat']
			slip_entity.arrival_date = replace_data['arrival_date']

			slip_entity.put()

			slip_dict = slip_entity.to_dict()
			slip_dict['kind'] = ndb.Key(urlsafe=id).kind()
			slip_dict['self'] = "/slips/" + id

			self.response.write(json.dumps(slip_dict))


	def delete(self, id=None):
		if id:
			ndb.Key(urlsafe=id).delete()



class slipWithBoatHandler(webapp2.RequestHandler):

	def put(self, id=None):
		if id:

			req_body = json.loads(self.request.body)
			slip_entity = ndb.Key(urlsafe=id).get()

			if slip_entity.current_boat is None and 'current_boat' in req_body and 'arrival_date' in req_body:

				boat_entity = ndb.Key(urlsafe=req_body['current_boat']).get()
				boat_entity.at_sea = False
				boat_entity.put()

				slip_entity.current_boat = req_body['current_boat']
				slip_entity.arrival_date = req_body['arrival_date']

				slip_entity.put()

				slip_dict = slip_entity.to_dict()
				slip_dict['kind'] = ndb.Key(urlsafe=id).kind()
				slip_dict['self'] = "/slips/" + id


				self.response.write(json.dumps(slip_dict))

			else:

				self.response.write('Error 403 Forbidden')
				self.response.set_status(403)



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
	('/slips', slipHandler),
	('/slips/(.*)/boat', slipWithBoatHandler),
    ('/slips/(.*)', slipHandler),
], debug=True)
