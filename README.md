# Py Cortex Intelligence 

## Release Notes
Need to consult the history of our project? [Click Here](CHANGELOG.md)

## How to build locale
```shell
pip install wheel
python setup.py bdist_wheel
```

## How to update on PIP
```
python -m twine upload  dist/*
```

## Cases of Use
### DataInput Parameters

```dictionary
data_input_parameters = {
    'ignoreValidationErrors': True/False,
}
// If you send this parameter, the datainput will ignore errors.
```
### Available Origins

```dictionary
execution_parameters = {
  'name': 'Name of your Integrations',
  'origin': 'Connector',
}

// If you send this to Execution your data need contain
// Dates in YYYY-MM-DD HH:MM:SS format
// Float numbers in XXX.XXX.XXX,YY format
// 'origin' are optional parameters, if you do not send the platform you will try to guess the formats
```

### If you need upload a file to Cortex Application
```python
from pycortexintelligence import functions as cortexfunctions

# Execution Parameters
# You can define Origin, to inform plataform a bundle of parses.
execution_parameters = {
    'name': 'LoadManager PyCortex',
    # 'origin': 'Connector',
}

# DataInput Parameters
data_input_parameters = {
    'ignoreValidationErrors': True,
}

# Loadmanager
loadmanager = 'https://api.cortex-intelligence.com'

# Timeouts
# You can set timeouts for the platform according to the size of the uploaded files
# or use the default
timeout = {
    'file': 300,
    'execution': 600,
}

# DataFormat are Optionally defined
dafault_data_format = {
    "charset": "UTF-8",
    "quote": "\"",
    "escape": "\\",
    "delimiter": ",",
    "fileType": "CSV"
}

# Upload to Cortex
cortexfunctions.upload_to_cortex(
    cubo_id='',
    file_path='',
    plataform_url='CLIENT.cortex-intelligence.com',
    username='',
    password='',
    data_format=dafault_data_format,
    timeout=timeout,
    loadmanager=loadmanager,
    execution_parameters=execution_parameters,
)
```

### If you need download file from Cortex Application
```python
from pycortexintelligence import functions as cortexfunctions

# DataFormat are Optionally defined
dafault_data_format = {
    "charset": "UTF-8",
    "quote": "\"",
    "escape": "\/\/",
    "delimiter": ",",
}

# Select the headers from file
columns = ['Name of Column A', 'Name of Column B']

# OPTIONAL Filters
filters = [
    ['Name of Column A', 'Value'],
    ['Name of Column A', 'Value1|Value2|Value3'],
    ['Name of Column B', 'dd/mm/YYYY'],
    ['Name of Column B', 'dd/mm/YYYY-dd/mm/YYYY'],
]

# Download from Cortex
cortexfunctions.download_from_cortex(
    cubo_id='',
    file_path='',
    plataform_url='CLIENT.cortex-intelligence.com',
    username='',
    password='',
    data_format=dafault_data_format,
    columns=columns,
    filters=filters,
)
```
## Validating downloaded data from platform.

Now download_from_cortex function returns a variable with Content-Rows from the response header
```
content_rows = cortexfunctions.download_from_cortex(
    ...
)
```

## CLI Usage
```bash
cortex.py --help
```

### Examples

```bash
cortex.py startproject --name "Project Name" --sname safe_project_name
```

## How to Contribute

### Developers

Developers can access our development manual by [clicking here](CONTRIBUTING.md).

### Community

You can create a new Issue [clicking here](issues/new/choose), and we will start a description about the reported Bug or Feature. 
