from click.testing import CliRunner

from cli import commands
from cli import api

from . import factories


def test_commands(tmpdir):
    analysis = api.create_instance(
        'analyses',
        project_level_analysis=factories.ProjectFactory(),
        storage_url=tmpdir.strpath,
        status='FINISHED',
        **factories.AnalysisFactory(ran_by=None))

    path = tmpdir.join('test.path')
    path.write('not empty')

    runner = CliRunner()
    args = ['-fi', 'pk', analysis['pk']]
    runner.invoke(commands.processed_finished, args, catch_exceptions=False)
    analysis = api.get_instance('analyses', analysis['pk'])

    assert analysis['status'] == 'SUCCEEDED'
    assert analysis['storage_usage']

    runner = CliRunner()
    args = ['--key', analysis['pk'], '--status', 'STAGED']
    runner.invoke(commands.patch_status, args, catch_exceptions=False)
    analysis = api.get_instance('analyses', analysis['pk'])
    assert analysis['status'] == 'STAGED'

    runner = CliRunner()
    args = [
        '-fi', 'pk', analysis['pk'], '-f', 'pipeline.name', '-f', 'pipeline',
        '-f', 'carlos', '-f', 'invalid.nested_attr']

    result = runner.invoke(commands.get_attributes, args, catch_exceptions=False)
    assert analysis['pipeline']['name'] in result.output
    assert 'pipeline.name' in result.output
    assert '"name": ' in result.output
    assert 'INVALID KEY (carlos)' in result.output
    assert 'INVALID KEY (nested_attr)' in result.output

    runner = CliRunner()
    args = ['-fi', 'pk', analysis['pk'], '--pattern', '*.path']
    result = runner.invoke(commands.get_paths, args, catch_exceptions=False)
    assert tmpdir.strpath in result.output
    assert 'test.path' in result.output

    args = ['-fi', 'pk', analysis['pk']]
    result = runner.invoke(commands.get_paths, args, catch_exceptions=False)
    assert tmpdir.strpath in result.output
