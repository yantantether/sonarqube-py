from sonarqube.api import SonarQube
import os
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('examples/config.py')

# Sonarqube API
SONARQUBE_HOST = os.environ.get('SONAR_HOST')
SONARQUBE_PORT = os.environ.get('SONAR_PORT')
SONARQUBE_TOKEN = os.environ.get('SONAR_TOKEN')

logger.info("SonarQube at [%s:%s] using token [%s]", SONARQUBE_HOST, SONARQUBE_PORT, SONARQUBE_TOKEN)

sq = SonarQube(token=SONARQUBE_TOKEN, host=SONARQUBE_HOST, port=SONARQUBE_PORT)
