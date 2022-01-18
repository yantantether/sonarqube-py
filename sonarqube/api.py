"""
This module contains the SonarAPIHandler, used for communicating with the
SonarQube server web service API.
"""
import requests
import logging
from os import environ as env
from .exceptions import raise_for_status

logger = logging.getLogger('sonarqube.api')

class Endpoint:

    def __init__(self, path, response_item=None, pager=None):
        self.path = path
        self.response_item = response_item
        self.pager = pager


class Pager:

    def __init__(self, response_items, request_page_number='p', request_page_size='ps',
                 response_object='paging', response_page_index='pageIndex',
                 response_page_size='pageSize', response_total='total'):
        self.response_items = response_items
        self.request_page_number = request_page_number
        self.request_page_size = request_page_size
        self.response_object = response_object
        self.response_page_index = response_page_index
        self.response_page_size = response_page_size
        self.response_total = response_total

    def paging(self, response):
        return response[self.response_object] if self.response_object else response

    def page_index(self, response):
        return self.paging(response)[self.response_page_index]

    def page_size(self, response):
        return self.paging(response)[self.response_page_size]

    def total(self, response):
        return self.paging(response)[self.response_total]

    def has_next_page(self, response):
        if response:
            total = self.total(response)
            if total > 10000:
                total = 10000
            page_size = self.page_size(response)
            page_num = self.page_index(response)
            return page_num * page_size < total
        else:
            return True

    def next_page_number(self, response, data):
        page_number = self.page_index(response)
        data[self.request_page_number] = page_number + 1

    def items(self, response):
        return response[self.response_items]


class SonarQube:

    """
    Adapter for SonarQube's web service API.
    """
    # Default host is local
    DEFAULT_HOST = env.get('SONAR_HOST', 'http://localhost')
    DEFAULT_PORT = env.get('SONAR_PORT', 9000)
    DEFAULT_TOKEN = env.get('SONAR_TOKEN')
    DEFAULT_USER = env.get('SONAR_USERNAME')
    DEFAULT_PASSWORD = env.get('SONAR_PASSWORD')
    DEFAULT_BASE_PATH = ''

    AUTH_VALIDATION_ENDPOINT = Endpoint('/api/authentication/validate', response_item='valid')
    PROJECTS_CREATE_ENDPOINT = Endpoint('/api/projects/create', response_item='project')
    PROJECTS_DELETE_ENDPOINT = Endpoint('/api/projects/delete', response_item=None)
    PROJECTS_ENDPOINT = Endpoint('/api/projects/search', pager=Pager(response_items='components'))
    ISSUES_ENDPOINT = Endpoint('/api/issues/search', pager=Pager(response_items='issues'))
    MEASURES_ENDPOINT = Endpoint('/api/measures/component', response_item='component.measures')
    RULE_ENDPOINT = Endpoint('/api/rules/show', response_item='rule')
    QUALITYGATES_SELECT_ENDPOINT = Endpoint('/api/qualitygates/select', response_item=None)
    QUALITYGATES_PROJECT_STATUS_ENDPOINT = Endpoint('/api/qualitygates/project_status', response_item='projectStatus')
    QUALITYGATES_LIST_ENDPOINT = Endpoint('/api/qualitygates/list', pager=Pager(response_items='components'))
    QUALITYGATES_GET_BY_PROJECT_ENDPOINT = Endpoint('/api/qualitygates/get_by_project', response_item='qualityGate')
    QUALITYPROFILES_SEARCH_ENDPOINT = Endpoint('/api/qualityprofiles/search', response_item='profiles')
    QUALITYPROFILES_ADD_PROJECT_ENDPOINT = Endpoint('/api/qualityprofiles/add_project', response_item='profiles')

    def __init__(self, url=None, host=None, port=None, user=None, password=None,
                 base_path=None, token=None):
        """
        Set connection info and session, including auth (if user+password
        and/or auth token were provided).
        """
        self._url = self._to_url(url, host, port, base_path)
        self._token = token or SonarQube.DEFAULT_TOKEN
        self._user = user or SonarQube.DEFAULT_USER
        self._password = password or SonarQube.DEFAULT_PASSWORD
        self._session = requests.Session()
        self._auth()
        logger.info(f'SonarQube at [{self._url}]')

    def _auth(self):
        # Prefer revocable authentication token over username/password if
        # both are provided
        if self._token:
            logger.info('Authenticating with token')
            self._session.auth = self._token, ''
        elif self._user and self._password:
            logger.info('Authenticating with username/password')
            self._session.auth = self._user, self._password
        else:
            logger.info('Authentication not set')
            
    def _to_url(self, url=None, host=None, port=None, base_path=None):
        if (url):
            return url
        return f'{host or SonarQube.DEFAULT_HOST}:{port or SonarQube.DEFAULT_PORT}{base_path or SonarQube.DEFAULT_BASE_PATH}'
        
        
    def endpoint_url(self, endpoint):
        """
        Return the complete url including host and port for a given endpoint.

        :param endpoint: service endpoint as str
        :return: complete url (including host and port) as str
        """
        return f'{self._url}{endpoint.path}'

    def post(self, endpoint, **data):
        return self.call(self._session.post, endpoint, **data)
        
    def get(self, endpoint, **data):
        return self.call(self._session.get, endpoint, **data)
        
    def delete(self, endpoint, **data):
        return self.call(self._session.delete, endpoint, **data)
        
    def call(self, method, endpoint, **data):

        res = method(self.endpoint_url(endpoint), stream=True, params=data or {})

        # Analyse response status and return or raise exception
        # Note: redirects are followed automatically by requests
        raise_for_status(res)
        
        # OK, return http response
        json = None
        if (res.text):
            json = res.json()
            if endpoint.response_item:
                for item in endpoint.response_item.split('.'):
                    if item in json:
                        json = json[item]
                    else:
                        json = None
                        break
        return json

    def paged_get(self, endpoint, **data):

        qs = data.copy()
        pager = endpoint.pager
        res = None

        # Cycle through rules
        while pager.has_next_page(res):
            res = self.get(endpoint, **qs)

            pager.next_page_number(res, qs)

            # Yield items
            for item in pager.items(res):
                # print(item)
                yield item

    def get_authentication_validate(self):
        return self.get(SonarQube.AUTH_VALIDATION_ENDPOINT)

    def post_projects_create(self, **args):
        return self.post(SonarQube.PROJECTS_CREATE_ENDPOINT, **args)

    def post_projects_delete(self, **args):
        return self.post(SonarQube.PROJECTS_DELETE_ENDPOINT, **args)
    
    def get_projects_search(self, **args):
        return self.paged_get(SonarQube.PROJECTS_ENDPOINT, **args)

    def get_issues(self, **args):
        return self.paged_get(SonarQube.ISSUES_ENDPOINT, **args)

    def get_measures(self, **args):
        return self.get(SonarQube.MEASURES_ENDPOINT, **args)

    def get_rule(self, **args):
        return self.get(SonarQube.RULE_ENDPOINT, **args)

    def post_qualitygates_select(self, **args):
        return self.post(SonarQube.QUALITYGATES_SELECT_ENDPOINT, **args)

    def get_qualitygates_project_status(self, **args):
        return self.get(SonarQube.QUALITYGATES_PROJECT_STATUS_ENDPOINT, **args)

    def get_qualitygates_get_by_project(self, **args):
        return self.get(SonarQube.QUALITYGATES_GET_BY_PROJECT_ENDPOINT, **args)

    def get_qualityprofiles_search(self, **args):
        return self.get(SonarQube.QUALITYPROFILES_SEARCH_ENDPOINT, **args)

    def post_qualityprofiles_add_project(self, **args):
        return self.post(SonarQube.QUALITYPROFILES_ADD_PROJECT_ENDPOINT, **args)
    