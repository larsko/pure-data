# Random Master Data Generator for Pure
This tool creates random data for Pure in valid XML. Variable size datasets containing orgs and persons can be generated.

## Getting Started
1. Install Python 3 and pip if you have not already.
1. See `requirements.txt` for required Python modules. To install these modules, use `pip install -r requirements.txt`.
1. Download code above and put all files into the same working directory.
1. Download `commons.xsd`, `person.xsd` and `organisation.xsd` and place into the working directory. (Get these from the Pure Administrator)
1. Run `generator.py` while passing the desired parameters (use --help to get an overview of possible parameters).
1. Output orgs + person XML files.
1. Upload to Pure.

## Parameters
| Parameter | Defaults | Description |
| -- | -- | -- |
| --help | Display help. |
| --simple/--complex | --complex | Create simple or complex XML output. |
| --photos / --no-photos | --no-photos |  Whether to create photos for persons. Note: Disabled with --simple.|
| --persons_out | persons.xml | Persons output file. |
| --orgs_out | orgs.xml | Orgs output file. |
| --i_orgs | | Existing org structure file. |
| --persons | 1 | Number of persons to create. |
| --orgs | 1 | Maximum number of children to create at each level of the hierarchy (hierarchy always has tree-height = 2). |
| --submission | en-GB | Locale for submission. E.g. 'en-GB'. |
| --locale | en | Locale for data generation. E.g. 'en'. |
| --validate | false | Validate XML output. Requires the XSDs in working directory. |
| --excel/--no-excel | --no-excel | Output to Excel file. |

## Usage Notes
- Org types generated are: university, faculty and department. If other types are required, use the --i_orgs to input an existing org structure.
- If modifying the XSL files it is recommended to use --validate to ensure XML output conforms to the schema definition.
- Qualifications.json contains a pre-populated set of academic qualifications used by the script. This can be customized by fetching the classification scheme from the Pure API.
- Usage of classifications has been kept to a minimum, so it should not be necessary to customize a lot of classification schemes before uploading the XML files.

## Examples
Create Chinese orgs and 50 persons (some with photos) in the corresponding submission locale: 
```
python3 generator.py --persons 50 --locale zh --submission zh-CH --photos
```

Create a set of persons with Mexican locale based on an existing org hierarchy (filename existing_orgs.xml) and with US submission language:
```
python3 generator.py --locale es-mx --submission en-US --i_orgs existing_orgs.xml
```

## Acknowledgments
This script uses https://github.com/lk-geimfari/mimesis for data generation.
