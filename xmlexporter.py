import lxml.etree as ET
from xml.dom import minidom
import dicttoxml
import click

class XMLExporter:

	@classmethod
	def to_xml(self, dict, pretty = False):
		# we could just use ET, but minidom nice for pretty print
		if pretty:
			return minidom.parseString(dicttoxml.dicttoxml(dict)).toprettyxml(indent="   ") 

		return dicttoxml.dicttoxml(dict, custom_root = 'item', attr_type = False)

	@classmethod
	def dump_xml(self,dict,filename):
		xml_str=XMLExporter.to_xml(dict,pretty=True)
		ET.ElementTree(ET.fromstring(xml_str)).write(filename)

	#@classmethod
	def transform_to_xml(data, data_type, output_file, config, stylesheet, schema_file, batch = False):

		xml_str = ''
		xml_dom = None
		# we process persons in batches for better performance
		if batch:
			root = ET.Element('root')
			with click.progressbar(data, label = 'Coverting to XML...') as bar:
				for item in bar:
					root.append(ET.fromstring(XMLExporter.to_xml(item)))
			xml_dom = root
		else:
			xml_str = XMLExporter.to_xml(data, True)
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