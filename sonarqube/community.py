"""
This module contains classes to simplify handling of community edition SonarQube.

Branch support:
Community edition doesn't support branches, so this module lets you create a project
with an arbitrary suffix to the project name. 
It also simplifies delete of a 'branch' project.

Assign quality gates & profiles:
Given we may need to create multiple projects, one per branch, using the UI to assign quality profile and gate
can be tedious. This module simplifies this by assigning the gate at project creation.
"""
from .api import SonarQube
import logging

logger = logging.getLogger('sonarqube.community')

class Project(object):
    
    DEFAULT_SUFFIX = 'release'
    DEFAULT_NAME_DELIMITER = ' '
    
    def __init__(self, key, name, suffix=None, quality_gate=None, quality_profiles=None, name_delimiter=None, sq=None) -> None:
        super().__init__()
        self.key = key
        self.name = name
        self.suffix = suffix or Project.DEFAULT_SUFFIX
        self.quality_gate = quality_gate
        self.quality_profiles = quality_profiles
        self.name_delimiter = name_delimiter or Project.DEFAULT_NAME_DELIMITER
        self.full_key = '{}:{}'.format(self.key, self.suffix)
        self.full_name = '{}{}{}'.format(self.name, self.name_delimiter, self.suffix)
        self.sq = sq or SonarQube()
        self.sq_project = None
        self.sq_quality_profiles = None
    
    def read(self):
        self.sq_project = next(self.sq.get_projects_search(projects=self.full_key), None)

    def create_or_update(self):
        if (not self.sq_project):
            self.read()
        if (not self.sq_project):
            self.sq.post_projects_create(project=self.full_key, name=self.full_name)
            self.read()
        if (self.quality_gate):
            self.sq.post_qualitygates_select(gateName=self.quality_gate, projectKey=self.full_key)
        if (self.quality_profiles):
            self._assign_quality_profiles()
    
    def delete(self):
        if (not self.sq_project):
            self.read()
        if (self.sq_project):
            self.sq.post_projects_delete(project=self.full_key)
            self.read()

    def _assign_quality_profiles(self):
        for lang in self.quality_profiles.keys():
            profile = self.quality_profiles[lang]
            logger.info("Adding profile [%s] for language [%s]", profile, lang)
            self.sq.post_qualityprofiles_add_project(language = lang, project = self.full_key, qualityProfile = profile)
