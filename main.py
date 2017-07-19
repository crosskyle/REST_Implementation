# Author: Kyle Cross
# Date: 7/13/17
# Description: A REST API that stores boat and slip data in a Google Cloud datastore

from google.appengine.ext import ndb
import webapp2
import time
import json


class boat(ndb.Model):
	id = ndb.StringProperty()
	name = ndb.StringProperty(required=True)
	type = ndb.StringProperty()
	length = ndb.IntegerProperty()
	at_sea = ndb.BooleanProperty()


class boatHandler(webapp2.RequestHandler):

	def post(self):
		req_body = json.loads(self.request.body)

		if 'name' in req_body:
			new_boat = boat(name=req_body['name'], at_sea=True)

			if 'type' in req_body:
				new_boat.type = req_body['type']

			if 'length' in req_body:
				new_boat.length = req_body['length']

			new_boat.put()
			new_boat.id = str(new_boat.key.urlsafe())
			new_boat.put()

			boat_dict = new_boat.to_dict()
			boat_dict['kind'] = new_boat.key.kind()
			boat_dict['self'] = '/boats/' + new_boat.key.urlsafe()

			self.response.write(json.dumps(boat_dict))

		else:
			self.response.write('Provide the correct parameters.')
			self.abort(400)


	def get(self, id=None):
		if id:
			boat_data = ndb.Key(urlsafe=id).get()
			boat_dict = boat_data.to_dict()
			boat_dict['kind'] = ndb.Key(urlsafe=id).kind()
			boat_dict['self'] = "/boats/" + id
			self.response.write(json.dumps(boat_dict))

		else:
			boat_list = boat.query().fetch()

			res_list = []
			res_obj = {}

			for b in boat_list:
				b_dict = b.to_dict()
				b_dict['kind'] = "boat"
				b_dict['self'] = "/boats/" + str(b_dict['id'])
				res_list.append(b_dict)

			res_obj['kind'] = 'collection'
			res_obj['contents'] = res_list
			self.response.write(json.dumps(res_obj))


	def patch(self, id=None):
		if id:
			req_body = json.loads(self.request.body)
			boat_entity = ndb.Key(urlsafe=id).get()

			if len(req_body) <= 3:

				if 'name' in req_body:
					boat_entity.name = req_body['name']

				if 'type' in req_body:
					boat_entity.type = req_body['type']
				else:
					boat_entity.type = None

				if 'length' in req_body:
					boat_entity.length = req_body['length']
				else:
					boat_entity.length = None

				boat_entity.put()

				boat_dict = boat_entity.to_dict()
				boat_dict['kind'] = ndb.Key(urlsafe=id).kind()
				boat_dict['self'] = "/boats/" + id

				self.response.write(json.dumps(boat_dict))

			else:
				self.response.write('Too many fields given')
				self.abort(400)


	def put(self, id=None):
		if id:
			req_body = json.loads(self.request.body)

			if 'name' in req_body and 'type' in req_body and 'length' in req_body:
				boat_entity = ndb.Key(urlsafe=id).get()

				boat_entity.name = req_body['name']
				boat_entity.type = req_body['type']
				boat_entity.length = req_body['length']

				boat_entity.put()

				boat_dict = boat_entity.to_dict()
				boat_dict['kind'] = ndb.Key(urlsafe=id).kind()
				boat_dict['self'] = "/boats/" + id

				self.response.write(json.dumps(boat_dict))

			else:
				self.response.write('All properties must be provided.')
				self.abort(400)


	def delete(self, id=None):
		if id:
			slip_with_boat_list = slip.query(slip.current_boat == id).fetch()

			if len(slip_with_boat_list) > 0:
				slip_with_boat = slip_with_boat_list[0]
				slip_with_boat.current_boat = None
				slip_with_boat.arrival_date = None
				slip_with_boat.put()

			ndb.Key(urlsafe=id).delete()
			time.sleep(.2)
			self.response.set_status(204)


class slip(ndb.Model):
	id = ndb.StringProperty()
	number = ndb.IntegerProperty(required=True)
	current_boat = ndb.StringProperty()
	arrival_date = ndb.StringProperty()


class slipHandler(webapp2.RequestHandler):

	def post(self):
		req_body = json.loads(self.request.body)

		if 'number' in req_body:
			if slip.query(slip.number == req_body['number']).get() is None:
				new_slip = slip(number=req_body['number'])

				new_slip.put()
				new_slip.id = str(new_slip.key.urlsafe())
				new_slip.put()

				slip_dict = new_slip.to_dict()
				slip_dict['kind'] = new_slip.key.kind()
				slip_dict['self'] = '/slips/' + new_slip.key.urlsafe()
				self.response.write(json.dumps(slip_dict))

			else:
				self.response.write('A unique slip number must be provided.')
				self.abort(400)

		else:
			self.response.write('A slip number must be provided.')
			self.abort(400)


	def get(self, id=None):
		if id:
			slip_data = ndb.Key(urlsafe=id).get()
			slip_dict = slip_data.to_dict()
			slip_dict['kind'] = ndb.Key(urlsafe=id).kind()
			slip_dict['self'] = "/slips/" + id
			self.response.write(json.dumps(slip_dict))

		else:
			slip_list = slip.query().fetch()
			res_list = []
			res_obj = {}

			for s in slip_list:
				s_dict = s.to_dict()
				s_dict['kind'] = "slip"
				s_dict['self'] = "/slips/" + str(s_dict['id'])
				res_list.append(s_dict)

			res_obj['kind'] = 'collection'
			res_obj['contents'] = res_list
			self.response.write(json.dumps(res_obj))


	def patch(self, id=None):
		if id:
			req_body = json.loads(self.request.body)
			slip_entity = ndb.Key(urlsafe=id).get()

			if len(req_body) <= 1:
				if 'number' in req_body:
					if slip.query(slip.number == req_body['number']).get() is None:
						slip_entity.number = req_body['number']

						slip_entity.put()

						slip_dict = slip_entity.to_dict()
						slip_dict['kind'] = ndb.Key(urlsafe=id).kind()
						slip_dict['self'] = "/slips/" + id

						self.response.write(json.dumps(slip_dict))

					else:
						self.response.write('A unique slip number must be provided.')
						self.abort(400)
				else:
					self.response.write('A slip number should be provided.')
					self.abort(400)
			else:
				self.response.write('Wrong parameters given.')
				self.abort(400)


	def put(self, id=None):
		if id:
			req_body = json.loads(self.request.body)
			slip_entity = ndb.Key(urlsafe=id).get()

			if len(req_body) < 1:
				if 'number' in req_body:
					if slip.query(slip.number == req_body['number']).get() is None:
						slip_entity.number = req_body['number']

						slip_entity.put()

						slip_dict = slip_entity.to_dict()
						slip_dict['kind'] = ndb.Key(urlsafe=id).kind()
						slip_dict['self'] = "/slips/" + id
						self.response.write(json.dumps(slip_dict))

					else:
						self.response.write('A unique slip number must be provided.')
						self.abort(400)
				else:
					self.response.write('A slip number should be provided.')
					self.abort(400)
			else:
				self.response.write('An input field must be provided')
				self.abort(400)


	def delete(self, id=None):
		if id:
			slip_entity = ndb.Key(urlsafe=id).get()

			if not (slip_entity.current_boat is None):
				boat_entity = ndb.Key(urlsafe=slip_entity.current_boat).get()
				boat_entity.at_sea = True
				boat_entity.put()

			ndb.Key(urlsafe=id).delete()
			time.sleep(.2)
			self.response.set_status(204)


class slipWithBoatHandler(webapp2.RequestHandler):

	def put(self, id=None):
		if id:
			req_body = json.loads(self.request.body)
			slip_entity = ndb.Key(urlsafe=id).get()

			if 'current_boat' in req_body and 'arrival_date' in req_body:

				if slip_entity.current_boat is None:
					boat_entity = ndb.Key(urlsafe=req_body['current_boat']).get()

					if boat_entity.at_sea is True:
						boat_entity.at_sea = False
						boat_entity.put()

						slip_entity.current_boat = req_body['current_boat']
						slip_entity.arrival_date = req_body['arrival_date']

						slip_entity.put()
						time.sleep(.7)

						slip_dict = slip_entity.to_dict()
						slip_dict['kind'] = ndb.Key(urlsafe=id).kind()
						slip_dict['self'] = "/slips/" + id + "/boat"


						self.response.write(json.dumps(slip_dict))

					else:
						self.response.write('Error 403 Forbidden')
						self.response.set_status(403)

				else:
					self.response.write('Error 403 Forbidden')
					self.response.set_status(403)

			else:
				self.response.write('current_boat and arrival_date must be in request body.')
				self.abort(400)


	def delete(self, id=None):
		if id:
			slip_entity = ndb.Key(urlsafe=id).get()

			if slip_entity.current_boat is None:
				self.response.write('This slip is already empty')
				self.abort(400)

			else:
				boat_entity = ndb.Key(urlsafe=slip_entity.current_boat).get()
				boat_entity.at_sea = True
				boat_entity.put()

				slip_entity.current_boat = None
				slip_entity.arrival_date = None
				slip_entity.put()

				slip_dict = slip_entity.to_dict()
				slip_dict['kind'] = ndb.Key(urlsafe=id).kind()
				slip_dict['self'] = "/slips/" + id + "/boat"
				self.response.write(json.dumps(slip_dict))


class MainPage(webapp2.RequestHandler):

	def get(self):
		self.response.write("A REST API for storing boat and slip data.")


def handle_400(request, response, exception):
	response.set_status(400)


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


app.error_handlers[400] = handle_400
