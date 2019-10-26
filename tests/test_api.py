import pytest
import json
import httpretty
from sonarqube.api import SonarQube
from sonarqube.api import Endpoint
from sonarqube.api import Pager
from sonarqube.exceptions import ClientError, AuthError, ValidationError, ServerError


def test_endpoint_url_should_use_port():
    sq = SonarQube(port=9001)
    assert "http://localhost:9001{}".format(sq.AUTH_VALIDATION_ENDPOINT.path) == \
        sq.endpoint_url(sq.AUTH_VALIDATION_ENDPOINT)


def test_endpoint_url_should_use_host():
    sq = SonarQube(host='http://myhost')
    assert "http://myhost:9000{}".format(sq.AUTH_VALIDATION_ENDPOINT.path) == \
        sq.endpoint_url(sq.AUTH_VALIDATION_ENDPOINT)


def test_endpoint_url_should_use_base_path():
    test = SonarQube(base_path='/testing')
    assert "http://localhost:9000/testing{}".format(test.AUTH_VALIDATION_ENDPOINT.path) == \
        test.endpoint_url(test.AUTH_VALIDATION_ENDPOINT)


@httpretty.activate
def test_get_response_400_should_raise_validation_error_with_message():

    httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                           body='{"errors":[{"msg":"error"}]}', status=400)
    with pytest.raises(ValidationError) as err:
        SonarQube().get(Endpoint('/endpoint'))
        assert 'error' in err.value


@httpretty.activate
def test_get_response_401_should_raise_auth_error():
    httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint', status=401)
    with pytest.raises(AuthError):
        SonarQube().get(Endpoint('/endpoint'))


@httpretty.activate
def test_get_response_403_should_raise_auth_error():
    httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint', status=403)
    with pytest.raises(AuthError):
        SonarQube().get(Endpoint('/endpoint'))


@httpretty.activate
def test_get_response_404_should_raise_client_error():
    httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint', status=404)
    with pytest.raises(ClientError):
        SonarQube().get(Endpoint('/endpoint'))


@httpretty.activate
def test_get_response_500_should_raise_server_error():
    httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint', status=500)
    with pytest.raises(ServerError):
        SonarQube().get(Endpoint('/endpoint'))


@httpretty.activate
def test_get_returns_response():
    httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                           body='{"hello":"world"}')
    assert 'world' == SonarQube().get(Endpoint('/endpoint'))['hello']


@httpretty.activate
def test_get_returns_item_in_response():
    httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                           body='{"item":{"hello":"world"}}')
    assert 'world' == SonarQube().get(Endpoint('/endpoint', response_item='item'))['hello']


@httpretty.activate
def test_paged_get_returns_single_page():
    httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint?p=1',
                           body=__paged_response(page_index=1, total=1))
    generator = SonarQube().paged_get(Endpoint('/endpoint', pager=Pager(response_items='items')))
    assert 1 == len(list(generator))


@httpretty.activate
def test_paged_get_returns_multiple_pages():
    httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint',
                           match_querystring=True,
                           body=__paged_response(page_index=1, total=2))
    httpretty.register_uri(httpretty.GET, 'http://localhost:9000/endpoint?p=2',
                           match_querystring=True,
                           body=__paged_response(page_index=2, total=2))
    generator = SonarQube().paged_get(Endpoint('/endpoint', pager=Pager(response_items='items')))
    assert 2 == len(list(generator))


def __paged_response(page_index=1, page_size=1, total=1):
    return json.dumps(
        {
            'paging': {
                'pageIndex': page_index,
                'pageSize': page_size,
                'total': total
                },
            'items': [{'hello': 'world'}]
        }
    )
