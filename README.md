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
import logging.config
from pycortexintelligence import functions as cortexfunctions

## Eh possivel utilizar o Graylog com o logging
## Podemos criar um filter para adicionar os campos 
## adicionais Application e tenant

class ApplicationTenantFilter(logging.Filter):
    def __init__(self, application_name, tenant):
        # In an actual use case would dynamically get this
        # (e.g. from memcache)
        self.Application = application_name
        self.tenant = tenant

    def filter(self, record):
        record.Application = self.Application
        record.tenant = self.tenant
        return True

## Criamos uma instancia do filter
cortexFilter = ApplicationTenantFilter(
    'App_Using_Pycortexintelligence',
    'CLIENT'
)

## Configurando o logging do sistema
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    "handlers": {
        'console':{
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        ## Entrada do handler do Graylog utilizando graypy
        ## Para utilizar esse handler eh necessario instalar o graypy 
        ## no requirements.txt de sua aplicacao ou com pip install graypy
        'graypy': {
            'class': 'graypy.GELFUDPHandler',
            'host': 'localhost',
            'port': 12201,
            'filters': [cortexFilter]
        }
    },
    "root": {
        "handlers": ["console", "graypy"],
        "level": "DEBUG",
    }
}
## Configuring Logging
logging.config.dictConfig(LOGGING)

# Execution Parameters
# You can define Origin, to inform platform a bundle of parses.
execution_parameters = {
    'name': 'LoadManager PyCortex',
    # 'origin': 'Connector',
}

# DataInput Parameters
data_input_parameters = {
    'ignoreValidationErrors': True,
}

# Timeouts
# You can set timeouts for the platform according to the size of the uploaded files
# or use the default
timeout = {
    'file': 300
}

# DataFormat are Optionally defined
default_data_format = {
    "charset": "UTF-8",
    "quote": "\"",
    "escape": "\\",
    "delimiter": ",",
    "fileType": "CSV",
    "compressed": "NONE"
}

try:
    # Upload to Cortex
    cortexfunctions.upload_to_cortex(
        cubo_id='',
        file_path='',
        plataform_url='CLIENT.cortex-intelligence.com',
        username='',
        password='',
        data_format=default_data_format,
        timeout=timeout,
        execution_parameters=execution_parameters,
    )
except Exception as e:
    # In case of error, send it to logger
    logging.error(str(e))

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
