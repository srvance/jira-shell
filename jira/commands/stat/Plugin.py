import curses
import argparse
from ..base import BaseCommand
from model import Release, KANBAN

class Command(BaseCommand):
    help = 'Print details of specified issues'
    usage = 'stat <issue_id>'
    examples = '''    stat 12345
    stat NG-12345
    '''

    def run(self, jira, args):
        if not args:
            print 'Error: you must specify an issue key'
            return
        parser = argparse.ArgumentParser()
        parser.add_argument('key')
        args = parser.parse_args(args)
        story = jira.cache.get(args.key)
        if not story:
            print 'Error: story key %s not found' % args.key
            return
        story = story[0]
        if not isinstance(story.__parent__, Release):
            print 'Error: story is not part of a release'
            return
        self.release = story.__parent__
        kanban = self.release.kanban()
        if not story:
            print 'No story matching key: %s' % args.key
            return
        print 'ID:', story.key
        print 'Release:', ', '.join(story.fix_versions)
        print 'Type:', story.type
        print 'Title:', story.title
        print 'Team:', story.scrum_team
        print 'Developer:', story.developer
        print 'Points:', story.points
        print 'Status:', story.status
        print 'Created:', story.created
        print 'Started:', story.started
        print 'Resolved:', story.resolved
        print 'Cycle Time:', story.cycle_time
        avg_ct = story.__parent__.kanban().average_cycle_time()
        ct = story.cycle_time
        sq_ct = story.__parent__.kanban().squared_cycle_times()
        if ct and avg_ct and sq_ct:
            spread = ct - avg_ct
            variance = spread * spread
            percent_variance = variance / sq_ct
            print '% Variance:', '%' + str(round(percent_variance, 4) * 100)
        else:
            print '% Variance:', 'nan'
        print 'Contingency:'
        print '    Inside:', kanban.contingency_inside(story.key)
        print '    Average:', kanban.contingency_average(story.key)
        print '    Outside:', kanban.contingency_outside(story.key)
        if story.history.data:
            print
            print 'Transition Log:'
            for t in story.history.all:
                backflow = ''
                if t[1] in KANBAN and t[2] in KANBAN:
                    if KANBAN.index(t[1]) > KANBAN.index(t[2]):
                        backflow = ' <- backflow'
                if not t[3]:
                    days = ''.ljust(3)
                else:
                    days = str(t[3]).ljust(3)
                print '    %s, [%s], %s -> %s %s' % (t[0], days, t[1], t[2],
                    backflow)
        print
        for direction in ['out', 'in']:
            print 'Links %s:' % direction
            for links in story.links[direction]:
                print '  %s:' % links
                for link in story.links[direction][links].values():
                    print '    %s %s %s' % (link.key, link.type,
                        link.title[:60])
