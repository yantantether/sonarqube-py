import click
import logging
from requests import RequestException
from os import path
import yaml
from .api import SonarQube
from .community import Project
from .exceptions import CliException

# logging
logger = logging.getLogger()

pass_config = click.make_pass_decorator(Project, ensure=True)

@click.group()
@click.option('-c', 'config', help='Configuration file')
@click.option('-s', 'suffix', help='Suffix to use when managing SonarQube projects')
@click.option('-u', 'url', help='SonarQube url')
@click.option('-h', 'host', help='SonarQube host')
@click.option('-p', 'port', help='SonarQube port')
@click.option('-t', 'token', help='SonarQube personal access token')
@click.option('-l', 'log_level', help='Logging level')
@click.pass_context
def cli(ctx, config=None, suffix=None, url=None, host=None, port=None, token=None, log_level=None):
    logging.basicConfig(level=log_level or logging.INFO)
    sq = SonarQube(url=url, host=host, port=port, token=token)
    ctx.obj = read_project(file=config, suffix=suffix, sq = sq)

@cli.command()
@pass_config
def create(project):
    try:
        project.create_or_update()
    except RequestException as e:
        logger.error(f"Error creating with status [{e.response.status_code if e.response else 'no response'}]: {e}")

@cli.command()
@pass_config
def delete(project):
    try:
        project.delete()
    except RequestException as e:
        logger.error(f"Error deleting with status [{e.response.status_code}]: {e}")

def read_project(file = None, suffix = None, sq = None):
    config_filename = file or ".sonarqube.yml"
    if (not path.isfile(config_filename)):
        raise CliException(f"Sonarqube config file missing: [{config_filename}]")
    with open(config_filename, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            config_project = config['project']
            return Project(
                key = config_project['key'],
                name = config_project['name'],
                suffix = suffix,
                quality_gate = config_project['quality-gate'],
                quality_profiles = config_project['quality-profiles'] or {},
                sq = sq
            )
        except yaml.YAMLError as exc:
            raise CliException("Failed to parse config file [%s] %s".format(config_filename, exc))

if __name__ == "__main__":
    cli()
