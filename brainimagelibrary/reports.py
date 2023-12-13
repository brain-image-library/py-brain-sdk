from .retrieve import *
from tqdm import tqdm
from pathlib import Path
from datetime import datetime

def __get_did(bildid):
	try:
		metadata = by_id(bildid=bildid)
		metadata =  metadata['retjson'][0]

		data = {}
		data['metadata_version'] = metadata['Submission']['metadata']
		data['bildid'] = bildid
		data['bildate'] = metadata['Submission']['bildate']
		data['contributor'] = metadata['Contributors'][0]['contributorname']
		data['affiliation'] = metadata['Contributors'][0]['affiliation']
		data['award_number'] = metadata['Funders'][0]['award_number']
		data['project'] = metadata['Submission']['project']
		data['consortium'] = metadata['Submission']['consortium']
		data['bildirectory'] = metadata['Dataset'][0]['bildirectory']
		data['generalmodality'] = metadata['Dataset'][0]['generalmodality']
		data['technique'] = metadata['Dataset'][0]['technique']
		data['species'] = metadata['Specimen'][0]['species']
		data['taxonomy'] = metadata['Specimen'][0]['ncbitaxonomy']
		data['genotype'] = metadata['Specimen'][0]['genotype']
		data['samplelocalid'] = metadata['Specimen'][0]['samplelocalid']

		return data
	except:
		print(f'Unable to process dataset {bildid}')
		return {}

def daily():
	directory = 'reports'
	today = datetime.today().strftime('%Y%m%d')
	output_filename = f'{directory}/{today}.tsv'

	if Path(output_filename).exists():
		print(f'Daily report {output_filename} found on disk.')
		df = pd.read_csv(output_filename, sep='\t')
		return df

	data = []

	print(f'Processing datasets in metadata version 1.0')
	v1 = by_version(version='1.0')
	for dataset in tqdm(v1):
		data.append(__get_did(dataset))

	print(f'Processing datasets in metadata version 2.0')
	v1 = by_version(version='2.0')
	for dataset in tqdm(v1):
		data.append(__get_did(dataset))

	df = pd.DataFrame(data)

	directory = 'reports'
	if not Path(directory).exists():
		Path(directory).mkdir()

	today = datetime.today().strftime('%Y%m%d')
	output_filename = f'{directory}/{today}.tsv'

	if not Path(directory).exists():
		Path(directory).mkdir()
	df.to_csv( output_filename, sep='\t', index=False)

	return df