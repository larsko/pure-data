#!/usr/bin/env python3
# pipreqs . --force to update requirements
# Random data generator for Pure

from mimesis import Generic
from mimesis.enums import *

import datetime as dt
from random import randint
from dateutil import parser as dateparser
import random

import os
import jsonpickle as json

import lxml.etree as ET
from xml.dom import minidom

from html import escape
import dicttoxml

import click

# Generates persons
class PersonGenerator:
	def __init__(self, organisations, provider):
		self.provider = provider
	
		self.organisations = organisations # org IDs
		self.person = provider.person
		self.address = provider.address
		self.datetime = provider.datetime
		self.internet = provider.internet
		self.text = provider.text
		self.cryptographic = provider.cryptographic
		self.file = provider.file
		self.numbers = provider.numbers
		self.business = provider.business

	genders = { 0: "unknown", 1: "male", 2: "female", 9: "unknown" }
	
	def gender(self, iso):
		return self.genders[iso]

	# job description values - only supports this as text, not classification ATM
	titles = ["Associate Professor", "Professor", "Director", "Researcher", "Adjunct", "Post-doc"]
	visibility = ["Public", "Restricted"]
	job_titles = ["doctor", "professor"]
	# types of associations
	association_types = [
		"staffOrganisationAssociation",
		"visitingOrganisationAssociation",
		"honoraryOrganisationAssociation",
		"studentOrganisationAssociation"]

	staff_types = ["academic", "nonacademic"]
	employment = ["academic", "honorary", "guestresearcher", "researcher"]

	def flip_coin(self):
		return random.choice([True, False])

	# Creates a list of randomized affiliations, can be set to include former affiliations.
	def create_affiliations(self, person_id, age, create_former = False, max_affiliations = 3):

		result = []
		primary_free = True
		# create 1 to max affilitations
		for i in range(0, randint(1, max_affiliations)):

			is_primary = self.flip_coin()
			
			# set start and end. former enabled and coin flip, then use the end date
			offset = dt.datetime.today().year - self.numbers.between(1, age)

			start_date = self.datetime.date(start = offset) 
			end_date = self.datetime.date(start = start_date.year) 

			# swap dates if they are wrong
			if start_date > end_date:
				tmp = end_date
				end_date = start_date
				start_date = tmp

			org_id = random.choice(self.organisations)
			aff_id = "{0}_{1}_{2}".format(person_id, org_id, i)

			association = {
				"id": aff_id,
				"organisation_id": org_id,
				"start": start_date,
				"end": end_date if (create_former and self.flip_coin()) else '',
				"job_title": random.choice(self.job_titles),
				"job_description": random.choice(self.titles),
				"primary": str(is_primary and primary_free).lower(),
				"employment": random.choice(self.employment), # this might not make much sense 
				"type": random.choice(self.staff_types),
				"association": random.choice(self.association_types)
			}

			# include additional complex stuff by random
			if self.flip_coin():
				association["emails"] = {
					"id": "{0}_email".format(aff_id),
					"value":self.person.email()
				}
			if self.flip_coin():
				association["phone_numbers"] = {
					"id":"{0}_phone".format(aff_id),
					"value": self.person.telephone()
				}
			if self.flip_coin():
				association["websites"] = {
					"id":"{0}_www".format(aff_id),
					"value": self.internet.home_page()
				}

			result.append(association)

			# if we already set a primary, disable this option
			if is_primary:
				primary_free = False

		return result

	# create a dict for each person, export JSON, convert to XML
	# We use escape() to encode all strings for XML usage.
	def create(self, complex = True):

		iso_gender = self.person.gender(iso5218=True)
		gen = Gender.FEMALE if iso_gender is 2 else Gender.MALE 

		first = escape(self.person.name(gen))
		middle =  escape(self.person.last_name(gen))
		last =  escape(self.person.last_name(gen))
		person_id = self.person.identifier(mask = '####################')

		result = {
			"id": person_id,
			"firstname": first + " " + middle,
			"lastname": last,
			"gender": self.gender(iso_gender)
		}

		# not everyone will have a knownas
		if self.flip_coin():
			result["names"] = {
				"knownas": {
					"firstname": "{0}. {1}.".format(first[0], middle[0]),
					"lastname": last
					}
			}

		# grab a random degree
		degree = self.degree()

		result["titles"] = {
			"postnominal": escape(degree["value"]) #self.person.title(gen, TitleType.ACADEMIC),
		}

		# date of birth between 16 and 66 years old
		# we use this to generate realistic affiliations
		age = self.person.age()
		dob = dt.datetime.today().year - age

		# TODO: Create meaningful job title + description
		# TODO: Lookup organisations in ID map from generated orgs
		result["organisationAssociations"] = self.create_affiliations(person_id, age, True)

		if complex:

			result["dob"] = self.datetime.date(start = dob, end = dob).strftime("%d-%m-%Y")

			result["nationality"] = self.address.country_code()

			# pick the first org as the start date
			result["employeeStartDate"] = next(iter(result["organisationAssociations"]))["start"].strftime("%d-%m-%Y")

			if self.flip_coin(): # Not everyone will have a photo
			#result["photo"] = self.person.avatar()
				result["photos"] = {  
					"portrait": {
						"id": self.cryptographic.uuid(),
						"url": self.internet.image_placeholder(width=300, height = 300),
						#"url": self.internet.stock_image(width=300, height = 300, keywords=['person', gen.value], writable = False),
						"filename": self.file.file_name(FileType.IMAGE).split(".")[0] + ".jpg"
						}
					}

			# a list of personal links and social media sites
			result["links"] = {
				"personal": {"url": self.internet.home_page(), "description": self.text.word()},
				"facebook": {"url": self.person.social_media_profile(site=SocialNetwork.FACEBOOK), "description": "facebook"},
				"twitter": {"url": self.person.social_media_profile(site=SocialNetwork.TWITTER), "description": "twitter"},
				"personal": {"url": self.person.social_media_profile(site=SocialNetwork.INSTAGRAM), "description": "Instagram"}
			}

			result["ids"] = [
				{ "type": "employee", "id": self.person.identifier(mask='######')},
				{ "type": "scopusauthor", "id": self.person.identifier(mask='##########')},
				{ "type": "mendeleyprofile", "id": self.cryptographic.uuid()}
			]

			# External positions, Academic qualifications, etc
			# Approximating the start and end based on age - degree type not taken into account...

			# idea: add function to easily skew dates randomly
			start_date = self.datetime.date(start = dob+18, end = dob+20)
			end_date = self.datetime.date(start = start_date.year+3, end = start_date.year+9)# finish degree age 23-30

			result["external_positions"] = [
				{
				"id": "{0}_ext".format(person_id),
				"appointment": escape(self.person.occupation()), 
				"organisation": escape(self.business.company()), 				
				"start_date": date_split(start_date),
				"end_date": date_split(end_date), 
				}
			]

			result["education"] = {
				"id": "{0}_edu".format(person_id),
				"start_date": date_split(start_date), # start degree age 18-20
				"end_date": date_split(end_date), 
				"academic_degree": escape(self.person.academic_degree()), #degree["value"], 
				"award_date": end_date.strftime("%d-%m-%Y"), # for simplicity, same as end
				"project": escape(self.text.title()),
				"organisation": escape(self.person.university()) # decide to choose an internal or create a random external one
			}

			if self.flip_coin():
				result["profile_information"] = {
					"id": "{0}_profile".format(person_id),
					"text": escape(self.text.text(10))
				}

			if self.flip_coin():
				result["phd_research_projects"] = escape(self.text.sentence())

			# maybe the are willing or not, so flip twice
			if self.flip_coin():	
				result["willingness_to_phd"] = str(self.flip_coin()).lower()

			# Home address
			result["privateAddress"]  = {
				"address": escape(self.address.address()),
				"city": escape(self.address.city()),
				"zip": escape(self.address.zip_code()),
				"state": escape(self.address.state()),
				"room": escape(self.address.street_number()),
				"building": escape(self.address.street_suffix()),
				"country": escape(self.address.country_code())
			}

			# User - probably not necessary
			#result["user"] = {"userName": self.person.username(), "email": self.person.email()}
			# ORCID - generation needs to be more advanced, since Pure validates it, oh well.
			#result["orcid"] = self.person.identifier(mask = '####-####-####-####')
		
		result["visibility"] = random.choice(self.visibility) #consider just using public...
		result["profiled"] = str(self.flip_coin()).lower()

		return result

	qualifications = []
	# TODO: make this generic to load any classification scheme in JSON...
	def degree(self):
		if len(self.qualifications)==0:
			if(os.path.exists('qualifications.json')):
				with open('qualifications.json', 'rb') as f:
					data = json.decode(f.read())
					for item in data["containedClassifications"]:
						degree = {
							"uri":item["uri"].split("qualification/")[1], 
							"value": item["terms"][0]["value"]
						}
						# discard top-level keys - they wont work...
						if "/" in degree["uri"]:
							self.qualifications.append(degree)

		return random.choice(self.qualifications)

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

	def create(self, type = 'university', complex = True):
		
		id = self.create_id()
		# associate the created id with a type, so we can filter IDs on org types if needed
		self.ids[id] = type
		# create an org with a random name
		org = { 
			"id": id, 
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

			child = self.create(self.types[depth])

			root["children"].append(child)

			# if we have more levels to go, make recursive call, same minimum
			if(depth + 1 < len(self.types)):
				self.create_hierarchy(child, depth + 1, min_children, new_max)	

		return root	

# break date into 3 components
def date_split(date):
	return {
		"y": date.year, 
		"m": date.month, 
		"d": date.day
	}

# Create the orgs and persons
# pass the base and submission language 
@click.command()
@click.option('--validate', default=False, help='Validate XML output.')
@click.option('--locale', default="en", help='Locale for data generation.')
@click.option('--submission', default="en_GB", help='Locale for submission.')
@click.option('--persons', default=1, help='Number of persons to generate.')
@click.option('--orgs', default=1, help='Number of child orgs to generate.')
@click.option('--i_orgs', default='', help='Input existing orgs from filename.')
@click.option('--orgs_out', default='orgs.xml', help='Orgs output file.')
@click.option('--persons_out', default='persons.xml', help='Persons output file.')
@click.option('--photos', default=False, help='Create photos for persons.')
@click.option('--simple', default=False, help='Create bare minimum XML output.')
def main(validate, locale, submission, persons, orgs, orgs_out, persons_out, i_orgs, photos, simple):

	click.echo(click.style("Creating random Pure master data", bold = True) )
	# set options
	cfg = {
		"validate": validate,
		"locale": locale,
		"submission": submission,
		"num_persons": persons,
		"num_orgs": orgs,
		"o_orgs": orgs_out,
		"o_persons": persons_out,
		"simple": simple,
		"photos": photos
	}

	# Mimesis - create provider with same language
	base_provider = Generic(cfg["locale"])

	# load org IDs from disk if we use an existing org dataset.
	org_ids = []
	if i_orgs:
		click.echo("Loading existing orgs...")
		org_ids = load_org_ids(i_orgs)
	else:
		click.echo("Creating orgs...")
		org_generator = OrganisationGenerator(base_provider)
		org_hierarchy = generate_orgs(org_generator, cfg)
		org_ids = org_generator.keys()

	generate_persons(PersonGenerator(org_ids, base_provider), cfg)

	click.echo(click.style("All done!",bold=True))

def generate_orgs(generator, config):
	result = generator.create_hierarchy(max_children = config["num_orgs"])
	transform(result, "orgs.xsl", config["o_orgs"], "organisation.xsd", config)
	return result

def generate_persons(generator, config):
	results = []
	count = config["num_persons"]
	with click.progressbar(range(0, count), label = 'Creating persons...') as bar:
		for i in bar:
			results.append(generator.create())
	transform(results, "persons.xsl", config["o_persons"], "person.xsd", config, True)

# to reload org IDs from previously generated dataset
# note: you can use any valid org XML file here
def load_org_ids(filename):
	ids = []
	xml = ET.parse(filename)
	for id in xml.xpath("//*[local-name()='organisationId']"):
		ids.append(id.text)
	return ids

def to_xml(dict, pretty = False):
	# we could just use ET, but minidom nice for pretty print
	if pretty:
		return minidom.parseString(dicttoxml.dicttoxml(dict)).toprettyxml(indent="   ") 

	return dicttoxml.dicttoxml(dict, custom_root = 'item', attr_type = False)


def transform(data, stylesheet, output_file, schema_file, config, batch = False):

	xml_str = ''
	xml_dom = None
	# we process persons in batches for better performance
	if batch:
		root = ET.Element('root')
		with click.progressbar(data, label = 'Coverting persons to XML...') as bar:
			for item in bar:
				root.append(ET.fromstring(to_xml(item)))
		xml_dom = root
	else:
		xml_str = to_xml(data, True)
		xml_dom = ET.fromstring(xml_str)

	transform = ET.XSLT(ET.parse(stylesheet))

	trans_xml = transform(xml_dom,		
		language = ET.XSLT.strparam(config["submission"].split("_")[0]), 
		country = ET.XSLT.strparam(config["submission"].split("_")[1]))

	# Save transformed XML file
	trans_xml.write(output_file, pretty_print = True, xml_declaration = True, encoding = "utf-8", standalone = True)

	# Validate output and emit errors
	if config["validate"]:
		schema = ET.XMLSchema( ET.parse(schema_file) )
		parser = ET.XMLParser(schema = schema)
		root = ET.parse(output_file, parser)

	click.echo(click.style("Transformation saved!",fg='green'))

main()