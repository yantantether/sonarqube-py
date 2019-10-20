# sonar-py

a set of scripts to ease interaction with SonarQube API

## Prerequisites

### Pipenv

This script library uses pipenv to set up Python and the required libraries.

Instructions to install pipenv here:
https://github.com/pypa/pipenv

### Docker

To help development it is useful to run SonarQube as a docker instance.

Use this command:

```
docker run -d --name sonarqube -p 9000:9000 sonarqube
```

### SonarQube configuration
