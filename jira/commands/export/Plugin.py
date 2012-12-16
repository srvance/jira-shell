import getopt
import curses

class Command(object):
    def run(self, jira, args):
        opts, args = getopt.getopt(args, '1:', ())
        print 'Retrieving data...'
        self.refresh_data(jira, False)
        kanban = self.release.kanban()
        stories = self.release.resolved_stories()
        stories.sort(key=lambda i:i.resolved)
        export_ct = open('export-ct.csv', 'w')
        export_ct.write(
            'Key, Points, Started, Resolved, Cycle Time, NSUL, NSUW, Average CT, NSLW, NSLL\r\n')
        average_cycle_time = kanban.average_cycle_time()
        for story in stories:
            if not story.started and story.resolved:
                continue
            export_ct.write(
                '%s, %.2f, %s, %s, %d, %.2f, %.2f, %.2f, %.2f, %.2f\r\n' % (
                story.key,
                story.points,
                story.started.strftime("%m/%d/%y"),
                story.resolved.strftime('%m/%d/%y'),
                story.cycle_time.days,
                average_cycle_time + (kanban.stdev_cycle_time() * 3),
                average_cycle_time + (kanban.stdev_cycle_time() * 2),
                average_cycle_time,
                average_cycle_time - (kanban.stdev_cycle_time() * 2),
                average_cycle_time - (kanban.stdev_cycle_time() * 3)))
        export_pt = open('export-pt.csv', 'w')
        export_pt.write(
            'Key, Cycle Time, Started, Resolved, Points, NSUL, NSUW, Average Pts, NSLW, NSLL\r\n')
        average_story_size = self.release.average_story_size()
        for story in stories:
            if not story.started and story.resolved:
                continue
            export_pt.write(
                '%s, %d, %s, %s, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f\r\n' % (
                story.key,
                story.cycle_time.days,
                story.started.strftime("%m/%d/%y"),
                story.resolved.strftime('%m/%d/%y'),
                story.points,
                average_story_size + (self.release.std_story_size() * 3),
                average_story_size + (self.release.std_story_size() * 2),
                average_story_size,
                average_story_size - (self.release.std_story_size() * 2),
                average_story_size - (self.release.std_story_size() * 3)))
        export_ratio = open('export-ratio.csv', 'w')
        export_ratio.write(
            'Key, Ratio, NSUL, NSUW, Average Ratio, NSLW, NSLL\r\n')
        average_story_size = self.release.average_story_size()
        for story in stories:
            if not story.started and story.resolved:
                continue
            export_pt.write(
                '%s, %d, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f\r\n' % (
                story.key,
                story.cycle_time.days/story.points,
                average_story_size + (self.release.std_story_size() * 3),
                average_story_size + (self.release.std_story_size() * 2),
                average_story_size,
                average_story_size - (self.release.std_story_size() * 2),
                average_story_size - (self.release.std_story_size() * 3)))


    def refresh_data(self, jira, refresh):
        self.release = jira.get_release(refresh)