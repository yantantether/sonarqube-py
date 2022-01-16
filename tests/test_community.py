import pytest
import json
import httpretty
from sonarqube.api import SonarQube
from sonarqube.community import Project

def test_no_suffix_name():
    
    # given
    project = Project(key="my-project", name='my-project', suffix=None)
    
    # when
    # project.create_or_update()
    
    # then
    assert project