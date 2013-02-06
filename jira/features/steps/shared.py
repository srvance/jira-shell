from behave import *
import model
import jira
import dao
from datetime import datetime

@given('The user is at the command line')
def step(context):
    context.release = model.Release()
    if not hasattr(context, 'table'):
        return
    for row in context.table:
        context.release.add(make_story(row))

@given('I have the following release')
def step(context):
    for row in context.table:
        dao.Jira.cache.data.root()[row['key']] = model.Release(row['key'])

@given('I have the following issues in the release')
def step(context):
    context.release = dao.Jira.cache.data.root()['1.0']
    for row in context.table:
        context.release.add(make_story(row))

@given('Issue "{issue_key}" has this transition history')
def step(context, issue_key):
    context.release = dao.Jira.cache.data.root()['1.0']
    issue = context.release[issue_key]
    for row in context.table:
        add_history(issue, row['date'], row['from'], row['to'])

@given('I have the json file "{some_file}" in the import directory')
def step(context, some_file):
    pass

@given('The file "{some_file}" is not in the import directory')
def step(context, some_file):
    pass

@given('I am in the directory "{command}"')
def step(context, command):
    dao.Jira.cache.cwd = command.split('/')
    dao.Jira.cache.cwd[0] = '/'

@when('I enter the command "{command}"')
def step(context, command):
    def mock_get_release(self=None, refresh=False):
        return context.release
    jira.get_release = mock_get_release
    dao.Jira.get_release = mock_get_release
    def mock_request_issue(self=None, refresh=False):
        return context.release.get('NG-' + command.split(' ')[1])
    jira.request_issue = mock_request_issue
    jira.dispatch(command)

@then('The REPL displays "{command}"')
def step(context, command):
    output = context.stdout_capture.getvalue()
    print output
    assert command in output

@then('I see these issues listed')
def step(context):
    output = context.stdout_capture.getvalue()
    for row in context.table:
        assert row['title'] in output

@then('I see "{value}" in the output')
def step(context, value):
    assert value in context.stdout_capture.getvalue()

@then('I do not see "{value}" in the output')
def step(context, value):
    assert value not in context.stdout_capture.getvalue()

def make_story(row):
    story = model.Story()
    story.key = row['key']
    story.title = row['title']
    story.components = []
    if 'team' in row.headings:
        story.scrum_team = row['team']
    else:
        story.scrum_team = 'unspecified'
    if 'dev' in row.headings:
        story.developer = row['dev']
    else:
        story.developer = 'unspecified'
    if 'points' in row.headings:
        story.points = float(row['points'])
    else:
        story.points = 1.0
    if 'created' in row.headings and row['created']:
        date = row['created'].split('/')
        story.created = datetime(2000+int(date[0]), int(date[1]), int(date[2]))
    else:
        story.created = None
    story.history = model.History()
    if 'started' in row.headings and row['started']:
        date = row['started'].split('/')
        story.history.data.append((
            datetime(2000+int(date[0]), int(date[1]), int(date[2])),
            1, 3))
    if 'resolved' in row.headings and row['resolved']:
        if not row['resolved']:
            return
        date = row['resolved'].split('/')
        story.history.data.append((
            datetime(2000+int(date[0]), int(date[1]), int(date[2])),
            3, 6))
    if 'status' in row.headings:
        story.status = int(row['status'])
    else:
        story.status = 3
    if 'type' in row.headings:
        story.type = row['type']
    else:
        story.type = '72'
    if 'fix' in row.headings:
        story.fix_versions = row['fix'].split(',')
    else:
        story.fix_versions = []
    return story

def add_history(issue, date, start, end):
    date = date.split('/')
    issue.history.data.append((
        datetime(2000+int(date[0]), int(date[1]), int(date[2])), start, end))
