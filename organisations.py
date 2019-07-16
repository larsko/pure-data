
from mimesis.enums import *
from html import escape
from random import randint
import random
import jsonpickle as json
import datetime as dt

# Generates orgs
class OrganisationGenerator:
	def __init__(self, provider, types = []):
		self.provider = provider

		# Use dishes for easy to remember org IDs.
		self.business = provider.business
		self.crypto = provider.cryptographic
		self.text = provider.text
		self.datetime = provider.datetime

		self.types = types if types else OrganisationGenerator.DEFAULT_TYPES 

	# the generated org IDs
	ids = {}
	def keys(self):
		return list(self.ids.keys())

	# org type classifications - TODO: Support config file
	DEFAULT_TYPES = ['university', 'faculty', 'department']

	def create_id(self):
		return self.crypto.hash(Algorithm.MD5)

	def create(self, type = 'university', parent_id = None, complex = True):
		
		id = self.create_id()
		# associate the created id with a type, so we can filter IDs on org types if needed
		self.ids[id] = type
		# create an org with a random name
		org = { 
			"id": id, 
			"parent_id": parent_id,
			"type": type, 
			"name": escape(self.business.company()), 
			"start_date": self.datetime.date(start = 1975).strftime("%d-%m-%Y"),
			"children": [] } 
		return org

	# takes a root org and builds a random tree-based hierarchy following the order of types
	def create_hierarchy(self, root = None, depth = 1, min_children = 1, max_children = 10):
		
		if root is None:
			root = self.create()

		# set seed to 1, so we get at least 1 child per layer - otherwise we can get very small structures
		new_max = randint(min_children, max_children)
		# add number of desired children to each  level
		for x in range(0, new_max):
			child = self.create(self.types[depth], root['id'])
			root["children"].append(child)
			# if we have more levels to go, make recursive call, same minimum
			if(depth + 1 < len(self.types)):
				self.create_hierarchy(child, depth + 1, min_children, new_max)	
		return root	