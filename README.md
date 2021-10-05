# sonarqube-py

A class library and CLI to ease interaction with [SonarQube](https://www.sonarqube.org/) API.

Although this project was written from scratch, it was made possible by understanding
the previous work of https://github.com/kako-nawao/python-sonarqube-api

## Prerequisites

### Pipenv

This script library uses pipenv to set up Python and the required libraries.

Instructions to install pipenv here:
https://github.com/pypa/pipenv

### Docker

To help development it is useful to run SonarQube as a docker instance.

Use this command:

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube
```

## SonarQube API Docs

SonarQube API docs are not easy to find: They are only available from a running instance of SonarQube.

If you are running sonarqube on localhost try this link:

    http://localhost:9000/web_api/

If you have access to sonarcloud, try this:

    https://sonarcloud.io/web_api
    
## Usage

import the SonarQube class from the sonarqube.api module:

```python
from sonarqube.api import SonarQube
```

instantiate the class, and execute any of the supported endpoints:

```python
sq = SonarQube(token=token, host=host, port=port)
```

## Endpoints

sonarqube-py supports the following endpoints:

* get_authentication_validate
* get_projects_search
* get_issues
* get_measures
* get_rule
* get_qualitygates_project_status
* get_qualitygates_get_by_project
* get_qualityprofiles_search

All endpoints support parameters as defined in the sonarqube wep-api documentation. 
I.e. the python client simply passes through any arguments you provide through to the web service API. 

## Examples

```python
python -m examples.measures
```
