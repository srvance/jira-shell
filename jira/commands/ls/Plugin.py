import getopt
import argparse
from ..base import BaseCommand

class Command(BaseCommand):
    help = 'List issues in a release'
    usage = 'ls [team] [-s status [status...]] [-t issue_type [issue_type...]] [-p [point]]'
    options_help = '''    -s : Show only issues with the specified status
    -t : Show only issues of the specified type
    -p : Show issues with the specified point estimates
    '''
    examples = '''    ls
    ls App
    ls Math -s 3 -t 72'''

    def run(self, jira, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', nargs='*', required=False)
        parser.add_argument('-t', nargs='*', required=False)
        parser.add_argument('-p', nargs='*', required=False)
        parser.add_argument('team', nargs='?')
        try:
            args = parser.parse_args(args)
        except:
            return
        self.refresh_data(jira, False)
        print 'Team:'.ljust(18), \
              'Pts:'.ljust(5), \
              'Stat:'.ljust(5), \
              'CT:'.ljust(5), \
              'Type:'.ljust(5), \
              'Title:'
        issues = 0
        points = 0
        query_points = []
        if args.p:
            query_points = [float(p) for p in args.p]
        hide_status = []
        show_status = []
        if args.s:
            for arg in args.s:
                if arg[:1] == '!':
                    hide_status.append(int(arg[1:]))
                else:
                    show_status.append(int(arg))
        hide_type = []
        show_type = []
        if args.t:
            for arg in args.t:
                if arg[:1] == '!':
                    hide_type.append(arg[1:])
                else:
                    show_type.append(arg)
        for story in sorted(self.release.data, key=lambda x: x.scrum_team):
            if show_status and story.status not in show_status:
                continue
            if hide_status and story.status in hide_status:
                continue
            if show_type and story.type not in show_type:
                continue
            if hide_type and story.type in hide_type:
                continue
            if args.p and story.points not in query_points:
                continue
            if not story.scrum_team:
                story.scrum_team = 'Everything Else'
            if args.team and story.scrum_team[:len(args.team)] != args.team:
                continue

            team = story.scrum_team
            if not team:
                team = 'Everything Else'
            if not story.cycle_time:
                cycle_time = 'None'
            elif not story.resolved:
                cycle_time = str(story.cycle_time) + '>'
            else:
                cycle_time = str(story.cycle_time)
            print team[:18].ljust(18), \
                  str(story.points).ljust(5), \
                  str(story.status).ljust(5), \
                  cycle_time.ljust(5), str(story.type).ljust(5), \
                  story.title[:37]
            issues += 1
            if story.points:
                points += story.points
        print 'Total Issues: %d, Total Points: %d' % (issues, points)

    def refresh_data(self, jira, refresh):
        self.release = jira.get_release(refresh)
