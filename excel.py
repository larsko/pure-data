
import os
import pandas as pd
norm = pd.io.json.json_normalize
import click

class ExcelExporter:
	#def __init__(self):

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