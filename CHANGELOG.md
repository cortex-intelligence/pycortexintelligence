# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## [0.0.22] - 2023-05-04

### Added
- Adaptando nova API do Loadmanager que permite criar uma LoadExecution diretamente, sem precisar criar um DataInput.
- Fazendo verificação de cada chamada http com response.raise_status_code()
- Chamada para o upload_local_to_cube aguarda a load execution ser processada pela plataforma
  e informa se hove algum erro levantando uma Exception

## [0.0.21] - 2021-07-14

### Added
- New method for validating downloaded data from platform based on Content-Rows included in response headers.

## [0.0.20] - 2021-01-11

### Added
- Support to download from platform to handle data in memory using BytesIO.

## [Unreleased]

### Added
- CLI to Download Cube/Form from Cortex
- Release 0.1.0 as a Branch
- Releases as a Branch

### Changed
- Improve error handling of functions
- Adjust standardization of function nomenclature

## [0.0.17] - 2021-04-16

### Added
- Support for paramaters on datainput in upload function. View the docs.

### Fixed
- Scape parameter correct.

## [0.0.15] - 2021-03-11

### Added
- Support for paramaters on execution in upload function. View the docs.
```
execution_parameters = {'name': 'Name', 'origin': 'Origin is optional, view the docs'}
```

## [0.0.14] - 2021-02-26

### Added
- Support for custom loadmanagers in upload function. View the docs.
```
loadmanager = "https://api.cortex-intelligence.com"
```

## [0.0.13] - 2021-02-23

### Added
- Support for timeouts in upload function. View the docs.
```
timeout = {
    'file': 300,
    'execution': 600,
}
```

## [0.0.12] - 2021-01-13

### Added
- Support to multiple filters on Download Cube.

## [0.0.10] - 2020-12-22

### Changed
- On default project, dont delete the log file.

## [0.0.9] - 2020-12-14

### Added

- adding developer guidelines to contributions
- adding CHANGELOG.md file
- adding support to download file from Cortex Application

### Added

- create core/messages.py file to index messages

## [0.0.8] - 2020-10-30

### Changed

- using logging module instead of print()
- update on file creation to `utf-8`
- update README.md

### Added

- create core/messages.py file to index messages

## [0.0.7] - 2020-10-30

### Added

- creating a CLI for pycortexintelligence

```bash
cortex.py --help
```

## [0.0.6] - 2020-10-27

### Fixed

- fix bug with calling _upload_local_2_cube_ function.

## [0.0.5] - 2020-10-26

### Added

- added support to data_format on upload_to_cortex

```python
dafault_data_format = {
    "charset": "UTF-8",
    "quote": "\"",
    "escape": "\/\/",
    "delimiter": ",",
    "fileType": "CSV"
}
```

## [0.0.4] - 2020-10-13

### Added

- Create README.md

## [0.0.3] - 2020-10-13

### Added

- Using format to string concatenation.

## [0.0.2] - 2020-10-08

### Added

- Ajust requirements.txt file and configuration to [Pypi](https://pypi.org/)

## [0.0.1] - 2020-10-08

### Added

- Birth of the project in order to simplify the use of Cortex's APIs.

# TODO Version Compare
[unreleased]: 
