from sonarqube.api import SonarQube
from sonarqube.exceptions import ValidationError, ClientError
from sonarqube.community import Project
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('examples/projects.py')
sq = SonarQube()

def getTestProject():
    return next(sq.get_projects_search(projects="test"), None)

def logError(e):
    response = e.response
    logger.info("message=[%s] : status=[%s] : body=[%s]", e, response.status_code, response.text)

def create_delete_with_api():
    # create a test project if it doesn't exist
    if (not getTestProject()):
        sq.post_projects_create(name="test", project="test")

    # create a project that fails throws error
    try:
        sq.post_projects_create(name="test", project="test")
    except ValidationError as e:
        logError(e)
        
    # get the created project
    test_project = getTestProject()
    logger.info("Project created [%s]", test_project)
    assert test_project

    # delete the project
    sq.post_projects_delete(project=test_project['key'])
    test_project = getTestProject()
    logger.info("Project deleted [%s]", test_project)
    assert not test_project

    # delete a project that doesn't exist throw error
    try:
        sq.post_projects_delete(project="test")
    except ClientError as e:
        logError(e)

# create_delete_with_api()

try:
    project = Project(name="test", key="mygroup:test", suffix="my-branch", name_delimiter="-", 
                      quality_gate="Sonar way", quality_profiles={'java': 'NHSBSA 2022-01', 'js': 'Sonar way'})
    project.delete()
    project.create_or_update()
except ClientError as e:
    logger.error(e.response)