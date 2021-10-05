from sonarqube.api import SonarQube
import os

# Sonarqube API
SONARQUBE_HOST = os.environ.get('SONAR_HOST')
SONARQUBE_PORT = os.environ.get('SONAR_PORT')
SONARQUBE_TOKEN = os.environ.get('SONAR_TOKEN')
sq = SonarQube(token=SONARQUBE_TOKEN, host=SONARQUBE_HOST, port=SONARQUBE_PORT)
