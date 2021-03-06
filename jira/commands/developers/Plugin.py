import argparse
from ..base import BaseCommand
from model import Release

class Command(BaseCommand):
    help = 'List the developers working on the release'
    usage = 'developers'

    def run(self, jira, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('dir', nargs='?')
        try:
            args = parser.parse_args(args)
        except:
            return
        if args.dir:
            container = jira.cache.get_by_path(args.dir)
        else:
            container = jira.cache.get_by_path(jira.cache.cwd)
        if not isinstance(container, Release):
            print 'Error: Must navigate to a release. (hint: help cd)'
            return
        print 'Developer:'.ljust(25), '   Stories: Aggregate Cycle Time:'
        developers = container.developers()
        for developer in sorted(developers.keys()):
            if not developer:
                continue
            print developer.ljust(25), ': ', str(len(developers[developer])).ljust(8), str(sum([s.cycle_time for s in developers[developer] if s.cycle_time]))
        print 'Total:', str(len(developers))
