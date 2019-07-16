#!/usr/bin/env python3
# pipreqs . --force to update requirements
# Random data generator for Pure

from mimesis import Generic

import lxml.etree as ET
from xml.dom import minidom

import dicttoxml

import pandas as pd
import numpy as np

import click

norm = pd.io.json.json_normalize

from persons import PersonGenerator
from organisations import OrganisationGenerator

# Create the orgs and persons
# pass the base and submission language 

@click.option('--validate', default=False, help='Validate XML output. Requires XSD in working directory.')
@click.option('--locale', default="en", help='Locale for data generation. E.g. \'en\'.')
@click.option('--submission', default="en-GB", help='Locale for submission. E.g. \'en_GB\'.')
@click.option('--persons', default=1, help='Number of persons to generate.')
@click.option('--orgs', default=1, help='Number of child orgs to generate.')
@click.option('--i_orgs', default='', help='Input existing orgs from filename.')
@click.option('--orgs_out', default='orgs.xml', help='Orgs output file.')
@click.option('--persons_out', default='persons.xml', help='Persons output file.')
@click.option('--photos/--no-photos', default=False, help='Whether to create photos for persons. Disabled with simple.')
@click.option('--simple/--complex', default=False, help='Create simple or complex XML output.')
@click.option('--excel/--no-excel', default=False, help='Output to Excel file.')
@click.command()
def main(validate, locale, submission, persons, orgs, orgs_out, persons_out, i_orgs, photos, simple, excel):
	
	click.echo(click.style("Creating random Pure master data", bold = True) )

	# set transformation to excel or xml
	t_persons = transform_to_excel if bool(excel) else transform_to_xml
	t_orgs = transform_orgs_to_excel if bool(excel) else transform_to_xml

	# set options
	cfg = {
		"validate": validate,
		"locale": locale.lower(),
		"submission": submission,
		"num_persons": persons,
		"num_orgs": orgs,
		"o_orgs": orgs_out,
		"o_persons": persons_out,
		"simple": bool(simple),
		"photos": bool(photos),
		"transform_persons": t_persons,
		"transform_orgs": t_orgs
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
	config['transform_orgs'](
		data=result, 
		data_type='organisations', 
		stylesheet="orgs.xsl", 
		output_file=config["o_orgs"], 
		schema_file="organisation.xsd", 
		config=config)

	return result

def generate_persons(generator, config):
	results = []
	count = config["num_persons"]
	with click.progressbar(range(0, count), label = 'Creating persons...') as bar:
		for i in bar:
			results.append(generator.create(config["simple"], config["photos"]))
	config['transform_persons'](
		data=results, 
		data_type='persons', 
		stylesheet="persons.xsl", 
		output_file=config["o_persons"], 
		schema_file="person.xsd", 
		config=config, 
		batch = True)

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

def transform_orgs_to_excel(data, output_file, config, data_type = '', stylesheet = '', schema_file = '', batch = False):

	df = pd.DataFrame()

	stack = [data]

	while(stack):
		item = stack.pop()
		df = pd.concat([df, norm(item).drop(['children'],axis=1)])
		stack.extend(item['children'])

	df.to_excel('orgs.xlsx', index = False)


# simple func to handle CSV to get raw data - yes arguments could be left out and changed to args... 
# this only works for persons
def transform_to_excel(data, output_file, config, data_type = '', stylesheet = '', schema_file = '', batch = False):

	writer = pd.ExcelWriter('{0}.xlsx'.format(data_type))

	# normalize all data
	df_main = norm(data)

	# output to other sheets
	dataframes = {}

	with click.progressbar(data, label = 'Converting to Excel...') as bar:
		for entry in bar:
			stack = list(entry.items())
			while stack:
				key, v = stack.pop()
				if type(v) is not str:
					if key not in dataframes:
						dataframes[key] = pd.DataFrame()		

					owner = pd.DataFrame({'{0}_id'.format(data_type):[entry['id']]})
					normalized = norm(v)

					# combine with the record ID for later lookup
					df_merged = normalized.assign(t=1).merge(owner.assign(t=1), how = 'outer').drop('t',1)

					dataframes[key] = pd.concat([dataframes[key], df_merged])
	
	# remove redundant columns
	to_drop = [c for c in df_main.columns for k in dataframes.keys() if k in c and k != 'id']
	df_main.drop(to_drop, axis=1, inplace=True)
	df_main.to_excel(writer, data_type, index = False)
	
	for df_k in dataframes.keys():
		dataframes[df_k].to_excel(writer, df_k, index=False)

	writer.save()
	click.echo(click.style("Transformation saved!",fg='green'))

def transform_to_xml(data, data_type, output_file, config, stylesheet, schema_file, batch = False):

	xml_str = ''
	xml_dom = None
	# we process persons in batches for better performance
	if batch:
		root = ET.Element('root')
		with click.progressbar(data, label = 'Coverting to XML...') as bar:
			for item in bar:
				root.append(ET.fromstring(to_xml(item)))
		xml_dom = root
	else:
		xml_str = to_xml(data, True)
		xml_dom = ET.fromstring(xml_str)

	transform = ET.XSLT(ET.parse(stylesheet))

	# Pure expects submission locale to be lower-UPPER.
	trans_xml = transform(xml_dom,		
		language = ET.XSLT.strparam(config["submission"].split("-")[0].lower()), 
		country = ET.XSLT.strparam(config["submission"].split("-")[1].upper()))

	# Save transformed XML file
	trans_xml.write(output_file, pretty_print = True, xml_declaration = True, encoding = "utf-8", standalone = True)

	# Validate output and emit errors
	if config["validate"]:
		schema = ET.XMLSchema( ET.parse(schema_file) )
		parser = ET.XMLParser(schema = schema)
		root = ET.parse(output_file, parser)

	click.echo(click.style("Transformation saved!",fg='green'))

main()