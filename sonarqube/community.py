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
    
    DEFAULT_KEY_DELIMITER = ':'
    DEFAULT_NAME_DELIMITER = ' '
    
    def __init__(self, key, name, suffix=None, quality_gate=None, quality_profiles=None,
                 key_delimiter=None, name_delimiter=None, sq=None) -> None:
        super().__init__()
        self.key = key
        self.name = name
        self.suffix = self.sanitise(suffix)
        self.quality_gate = quality_gate
        self.quality_profiles = quality_profiles
        self.full_key = self.format(self.key, key_delimiter or Project.DEFAULT_KEY_DELIMITER, self.suffix)
        self.full_name = self.format(self.name, name_delimiter or Project.DEFAULT_NAME_DELIMITER, self.suffix)
        self.sq = sq or SonarQube()
        self.sq_project = None
        self.sq_quality_profiles = None
    
    def read(self):
        self.sq_project = next(self.sq.get_projects_search(projects=self.full_key), None)
        if (self.sq_project):
            logger.info(f"Retrieved project [{self.full_key}] from SonarQube")

    def create_or_update(self):
        if (not self.sq_project):
            self.read()
        if (not self.sq_project):
            logger.info(f"Creating project [{self.full_key}]")
            self.sq.post_projects_create(project=self.full_key, name=self.full_name)
            self.read()
        if (self.quality_gate):
            logger.info(f"Assigning quality gate [{self.quality_gate}] to [{self.full_key}]")
            self.sq.post_qualitygates_select(gateName=self.quality_gate, projectKey=self.full_key)
        if (self.quality_profiles):
            self._assign_quality_profiles()
    
    def delete(self):
        if (not self.sq_project):
            self.read()
        if (self.sq_project):
            self.sq.post_projects_delete(project=self.full_key)
            self.read()

    def sanitise(self, value):
        # handling 'feature/branch' case for now
        # consider more sophisticated cleanup
        return value.replace('/', '-') if value else None
        
    def format(self, prefix, delimiter, suffix):
        return prefix if not suffix else f'{prefix}{delimiter}{suffix}'
        
    def _assign_quality_profiles(self):
        for lang in self.quality_profiles.keys():
            profile = self.quality_profiles[lang]
            logger.info(f"Assigning quality profile [{profile}] for language [{lang}] to [{self.full_key}]")
            self.sq.post_qualityprofiles_add_project(language = lang, project = self.full_key, qualityProfile = profile)
