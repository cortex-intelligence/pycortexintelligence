import os
from pycortexintelligence.core.config import OUTPUT_FOLDER, DOWNLOADED_FOLDER

FOLDERS = [OUTPUT_FOLDER, DOWNLOADED_FOLDER]
FILES = [
    'README.md',
    '.gitignore',
    '.dockerignore',
    '.env',
    'requirements.txt',
    'Dockerfile',
    'main.py',
]


def write_main_py():
    return """from pycortexintelligence.core.funcs_env import load_env_to_dict, verify_env, delete_temp_files

# Set specific variables to project
custom_variables = ['variable_1', 'variable_2']

# Script para pegar automaticamente as variavéis de ambiente.
OS_PARAMS = load_env_to_dict(new_params_to_check=custom_variables)
print('Criamos as variavéis de ambiente...')

# Valida se o OS_PARAMS está correto para esse projeto.
verify_env(OS_PARAMS, new_params_to_check=custom_variables)
print('Tudo indica sucesso para essa operação soldade, vamos que vamos! :)')

# Deleta os arquivos temporários e de output.
delete_temp_files(os_params=OS_PARAMS)
print('Deletamos os arquivos temporários, só pra prevenir né rs rs')

# TODO Define a project!
"""


def write_dockerfile():
    return """FROM python:3.9-alpine

# Set arguments
# Arguments of E-mail
ENV email_password=""
ENV email_port=""
ENV email_smtp=""
ENV email_user=""
ENV email_to_error=""
ENV project_name=""

# Arguments of Cortex
ENV plataform_url=""
ENV plataform_username=""
ENV plataform_password=""
ENV plataform_cube_id=""

# Arguments of Project
ENV param_s3_bucket=""
ENV param_s3_key=""
ENV param_s3_secret_key=""

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

## install dependencies
RUN set -xe \\
    && apk add --no-cache curl \\
    && apk --no-cache add curl gcc g++ libressl-dev libffi-dev make \\
    && curl -sSL https://bootstrap.pypa.io/get-pip.py | python \\
    && pip install wheel

# Directory Structure
RUN mkdir -p /code

# Set work directory.
WORKDIR /code

# Copy project code.
COPY ./ /code/

# Install dependencies.
RUN pip install -r requirements.txt

CMD python main.py
"""


def write_env(project_name):
    return """email_password=""
email_port=""
email_smtp=""
email_user=""
email_to_error=""
project_name="{}"
plataform_url=""
plataform_username=""
plataform_password=""
plataform_cube_id=""
""".format(project_name)


def write_dockerignore():
    return """### Padrão Cortex ###
# Arquivos Temporárops e de Output
downloaded_files/*
output/*
"""


def write_gitignore():
    return """# Created by https://www.toptal.com/developers/gitignore/api/python
# Edit at https://www.toptal.com/developers/gitignore?templates=python

### Padrão Cortex ###
# Arquivos Temporárops e de Output
downloaded_files/*
output/*
.env

### Python ###
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
pytestdebug.log

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/
doc/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
#.env
#.venv
#env/
#venv/
#ENV/
#env.bak/
#venv.bak/
#pythonenv*

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# profiling data
.prof

# End of https://www.toptal.com/developers/gitignore/api/python
"""


def write_readme_md(project_name, safe_name):
    return """# {}

**URL DO CONNECTOR:** ``

**CUBO:** -

**FORM:** -

**PERIODICIDADE:** -

**CLIENTE:** -

**DATA CONNECTION:** -

**DATA SOURCE:** ``

**CARGA TOTAL:** -

**CARGA INCREMENTAL:** -

**APAGA DADOS DO DESTINO:** -

**APAGA SOMENTE SE EXISTIREM NOVOS DADOS:** -

**CAMPOS ASSOCIADOS:**

`-` > `-`

**Descrição da Integração:**

- 

**Atenção**: 
 
- 

## How to test?

Create virtualenv and active it.

```shell
python -m venv {}
source {}/bin/activate
```

With the venv activated, you need install the requirements and run the project.
```
({}) pip install -r requirements.txt
({}) python main.py

```

## How to Build?

Build the container
```
docker build -t {} .
```

Run the container
```
docker run --rm {}
```
""".format(
        project_name,
        safe_name,
        safe_name,
        safe_name,
        safe_name,
        safe_name,
        safe_name,
    )


def check_create_dirs():
    for folder in FOLDERS:
        try:
            os.stat(folder)
        except FileNotFoundError:
            os.mkdir(folder)


def creck_create_files(project_name, safe_name):
    for file in FILES:
        with open(file, 'w') as f:
            if file == 'README.md':
                file_to_write = write_readme_md(project_name, safe_name)
                print('Writing README.md file...')
            elif file == '.gitignore':
                file_to_write = write_gitignore()
                print('Writing .gitignore file...')
            elif file == '.dockerignore':
                file_to_write = write_dockerignore()
                print('Writing .dockerignore file...')
            elif file == '.env':
                file_to_write = write_env(project_name)
                print('Writing .env file...')
            elif file == 'requirements.txt':
                file_to_write = ""
                print('Writing requirements.txt file...')
            elif file == 'Dockerfile':
                file_to_write = write_dockerfile()
                print('Writing Dockerfile file...')
            elif file == 'main.py':
                file_to_write = write_main_py()
                print('Writing main.py file...')
            else:
                print('Unknown file.')
            f.writelines(file_to_write)
