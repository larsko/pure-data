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

from persons import PersonGenerator
from organisations import OrganisationGenerator
from excel import ExcelExporter
from xmlexporter import XMLExporter

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
	t_persons = ExcelExporter.transform_to_excel if bool(excel) else XMLExporter.transform_to_xml
	t_orgs = ExcelExporter.transform_orgs_to_excel if bool(excel) else XMLExporter.transform_to_xml

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

main()