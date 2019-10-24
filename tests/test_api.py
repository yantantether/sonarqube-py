import unittest
import httpretty
import json
from unittest import TestCase
from sonarqube import SonarQube
from sonarqube.api import Endpoint
from sonarqube.api import Pager
import warnings

from sonarqube.exceptions import ClientError, AuthError, ValidationError, ServerError


class SonarQubeTest(TestCase):

    @staticmethod
    def paged_response(page_index=1, page_size=1, total=1):
        return json.dumps({
            'paging': {
                'pageIndex':page_index,
                'pageSize': page_size,
                'total': total
                },
            'items': [{'hello': 'world'}]
        })

    def setUp(self):
        self.h = SonarQube(user='admin', password='admin')
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*")

    def test_endpoint_url_should_use_port(self):
        test = SonarQube(port=9001)
        self.assertEqual(
            "http://localhost:9001{}".format(test.AUTH_VALIDATION_ENDPOINT.path),
            test._endpoint_url(test.AUTH_VALIDATION_ENDPOINT))

    def test_endpoint_url_should_use_host(self):
        test = SonarQube(host='http://myhost')
        self.assertEqual(
            "http://myhost:9000{}".format(test.AUTH_VALIDATION_ENDPOINT.path),
            test._endpoint_url(test.AUTH_VALIDATION_ENDPOINT))

    def test_endpoint_url_should_use_base_path(self):
        test = SonarQube(base_path='/testing')
        self.assertEqual(
            "http://localhost:9000/testing{}".format(test.AUTH_VALIDATION_ENDPOINT.path),
            test._endpoint_url(test.AUTH_VALIDATION_ENDPOINT))

    @httpretty.activate
    def test_get_response_400_should_raise_validation_error_with_message(self):

        httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                               body='{"errors":[{"msg":"error"}]}', status=400)
        with self.assertRaises(ValidationError) as context:
            SonarQube()._get(Endpoint('/endpoint'))
            self.assertTrue('error' in context.exception)

    @httpretty.activate
    def test_get_response_401_should_raise_auth_error(self):
        httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                               status=401)
        with self.assertRaises(AuthError) as context:
            SonarQube()._get(Endpoint('/endpoint'))

    @httpretty.activate
    def test_get_response_403_should_raise_auth_error(self):
        httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                               status=403)
        with self.assertRaises(AuthError) as context:
            SonarQube()._get(Endpoint('/endpoint'))

    @httpretty.activate
    def test_get_response_404_should_raise_client_error(self):
        httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                               status=404)
        with self.assertRaises(ClientError) as context:
            SonarQube()._get(Endpoint('/endpoint'))

    @httpretty.activate
    def test_get_response_500_should_raise_server_error(self):
        httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                               status=500)
        with self.assertRaises(ServerError) as context:
            SonarQube()._get(Endpoint('/endpoint'))

    @httpretty.activate
    def test_get_returns_response(self):
        httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                               body='{"hello":"world"}')
        self.assertEqual('world', SonarQube()._get(Endpoint('/endpoint'))['hello'])

    @httpretty.activate
    def test_get_returns_item_in_response(self):
        httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                               body='{"item":{"hello":"world"}}')
        self.assertEqual('world', SonarQube()._get(Endpoint('/endpoint', response_item='item'))['hello'])

    @httpretty.activate
    def test_paged_get_returns_single_page(self):
        httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint?p=1',
                               body=SonarQubeTest.paged_response(page_index=1, total=1))
        generator = SonarQube()._paged_get(Endpoint('/endpoint', pager=Pager(response_items='items')))
        self.assertEqual(1, sum(1 for item in generator))


    @httpretty.activate
    def test_paged_get_returns_multiple_pages(self):
        httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                               match_querystring=True,
                               body=SonarQubeTest.paged_response(page_index=1, total=2))
        httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint?p=2',
                               match_querystring=True,
                               body=SonarQubeTest.paged_response(page_index=2, total=2))
        generator = SonarQube()._paged_get(Endpoint('/endpoint', pager=Pager(response_items='items')))
        self.assertEqual(2, sum(1 for item in generator))


if __name__ == '__main__':
    unittest.main()
