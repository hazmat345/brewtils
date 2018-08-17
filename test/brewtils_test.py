import copy
import os

import pytest
from yapconf.exceptions import YapconfItemNotFound

import brewtils
import brewtils.rest
from brewtils.errors import ValidationError
from brewtils.rest.easy_client import EasyClient


class TestBrewtils(object):

    @pytest.fixture
    def params(self):
        return {
            'bg_host': 'bg_host',
            'bg_port': 1234,
            'ssl_enabled': False,
            'api_version': None,
            'ca_cert': 'ca_cert',
            'client_cert': 'client_cert',
            'url_prefix': '/beer/',
            'ca_verify': True,
            'username': None,
            'password': None,
            'access_token': None,
            'refresh_token': None,
        }

    def setup_method(self):
        self.safe_copy = os.environ.copy()

    def teardown_method(self):
        os.environ = self.safe_copy

    def test_load_config_cli(self):
        cli_args = ['--bg-host', 'the_host']

        config = brewtils.load_config(cli_args)
        assert config.bg_host == 'the_host'

    def test_load_config_cli_custom_argument_parser_vars(self):
        parser = brewtils.get_argument_parser()
        parser.add_argument('some_parameter')

        cli_args = ['param', '--bg-host', 'the_host']
        parsed_args = parser.parse_args(cli_args)

        config = brewtils.load_config(**vars(parsed_args))
        assert config.bg_host == 'the_host'
        assert parsed_args.some_parameter == 'param'
        assert 'some_parameter' not in config

    def test_load_config_cli_custom_argument_parser_cli(self):
        parser = brewtils.get_argument_parser()
        parser.add_argument('some_parameter')

        cli_args = ['param', '--bg-host', 'the_host']
        parsed_args = parser.parse_args(cli_args)

        config = brewtils.load_config(cli_args=cli_args, argument_parser=parser)
        assert config.bg_host == 'the_host'
        assert parsed_args.some_parameter == 'param'
        assert 'some_parameter' not in config

    def test_load_config_environment(self):
        os.environ['BG_HOST'] = 'the_host'

        config = brewtils.load_config([])
        assert config.bg_host == 'the_host'

    def test_load_config_extra_spec(self):
        os.environ['BG_HOST'] = 'the_host'
        os.environ['SOME_PARAMETER'] = 'param'

        spec = {
            "some_parameter": {
                "type": "str",
                "description": "Another required parameter",
                "env_name": "SOME_PARAMETER",
                "apply_env_prefix": False,
            },
        }

        config = brewtils.load_config(merge_specification=spec)
        assert config.some_parameter == 'param'

    def test_get_easy_client(self):
        client = brewtils.get_easy_client(host='bg_host')
        assert isinstance(client, EasyClient) is True

    def test_get_connection_info_kwargs(self, params):
        assert params == brewtils.get_connection_info(**params)

    def test_get_connection_info_env(self, params):
        os.environ['BG_HOST'] = 'bg_host'
        os.environ['BG_PORT'] = '1234'
        os.environ['BG_SSL_ENABLED'] = 'False'
        os.environ['BG_CA_CERT'] = 'ca_cert'
        os.environ['BG_CLIENT_CERT'] = 'client_cert'
        os.environ['BG_URL_PREFIX'] = '/beer/'
        os.environ['BG_CA_VERIFY'] = 'True'

        assert params == brewtils.get_connection_info()

    def test_get_connection_info_deprecated_kwargs(self, params):
        deprecated_params = copy.copy(params)
        deprecated_params['host'] = deprecated_params.pop('bg_host')
        deprecated_params['port'] = deprecated_params.pop('bg_port')

        assert params == brewtils.get_connection_info(**deprecated_params)

    def test_get_connection_info_deprecated_env(self, params):
        deprecated_params = copy.copy(params)
        deprecated_params['bg_host'] = None
        deprecated_params['bg_port'] = None
        deprecated_params['ca_cert'] = None
        deprecated_params['client_cert'] = None

        os.environ['BG_SSL_CA_CERT'] = 'ca_cert'
        os.environ['BG_SSL_CLIENT_CERT'] = 'client_cert'
        os.environ['BG_WEB_HOST'] = 'bg_host'
        os.environ['BG_WEB_PORT'] = '1234'

        assert params == brewtils.get_connection_info(**deprecated_params)

    def test_get_connection_info_no_host(self):
        with pytest.raises(ValidationError):
            brewtils.get_connection_info()

    def test_normalize_url_prefix(self, params):
        os.environ['BG_WEB_HOST'] = 'bg_host'
        os.environ['BG_URL_PREFIX'] = '/beer'

        generated_params = brewtils.get_connection_info()
        assert generated_params['url_prefix'] == params['url_prefix']
