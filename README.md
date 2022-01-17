# sonarqube-py

A class library and CLI to ease interaction with [SonarQube](https://www.sonarqube.org/) API.

Although this project was written from scratch, it was made possible by understanding
the previous work of <https://github.com/kako-nawao/python-sonarqube-api>

## Prerequisites

### Poetry

This script library uses [Poetry](https://python-poetry.org/) to set up Python and the required libraries.

Instructions to install Poetry here:

<https://python-poetry.org/docs/>

### Docker

To help development it is useful to run SonarQube as a docker instance.

Use this command:

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube
```

## SonarQube API Docs

SonarQube API docs are not so easy to find: They are available from a running instance of SonarQube.

If you are running sonarqube on localhost try this link:

<http://localhost:9000/web_api/>

If you have access to sonarcloud, try this:

<https://sonarcloud.io/web_api>

## Access control

Access to SonarQube API will require authentication by default.
You should use a Personal Access Token generated from the [SonarQube UI](https://docs.sonarqube.org/latest/user-guide/user-token/)

## Sonarqube-py CLI Usage

You can run a CLI that has been designed to support rudimentary management of a project within SonarQube.

### Configuration file

The CLI relies on a configuration file to define the project key, name and which quality profiles and gate to apply.

```yaml .sonarqube-ci.yml
---
project:
  key: sonarqube-py
  name: sonarqube-py
  quality-gate: "Sonar way"
  quality-profiles:
    py: "Sonar way"
    css: "Sonar way"
```

### Environment variables

You can configure behaviour using environment variables:

| env-var | meaning | default |
| ------- | ------- | ------- |
| SONAR_HOST | SonarQube host | `localhost` |
| SONAR_PORT | SonarQube port | `9000` |
| SONAR_TOKEN | SonarQube personal access token | |

### Command line args

You can also configure behaviour using command line arguments.
Command line arguments will override environment variables.

| flag | meaning | default |
| ---- | ------- | ------- |
| -c   | Configuration file | `.sonarqube-ci.yml` |
| -s   | Suffix to add to key and name when managing SonarQube projects | |
| -h   | SonarQube host | _see environment variables_ |
| -p   | SonarQube port | _see environment variables_ |
| -t   | SonarQube personal access token | |
| -l   | Logging level (ERROR/WARNING/INFO/DEBUG) | `INFO` |
| --help | Show help |

### Commands

| command | meaning |
| ------- | ------- |
| create  | create or update a project with specified quality gate and profiles |
| delete  | delete a project |

Command line args MUST be placed _before_ the command.

e.g.

```bash
python -m sonarqube.cli -c my-sonarqube-config.yml create
```

## Sonarqube-py API Usage

You can also use the API in code. Import the SonarQube class from the sonarqube.api module:

```python
from sonarqube.api import SonarQube
```

instantiate the class, and execute any of the supported endpoints:

```python
sq = SonarQube(host=host, port=port, token=token)
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

```bash
python -m examples.measures
````

```bash
python -m examples.projects
````
