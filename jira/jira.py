#!/usr/bin/env python2.7
import optparse
from dao import Jira
import commands
import os

command_plugins = {}
for plugin in os.listdir('/'.join(commands.__file__.split('/')[:-1])):
    if plugin in ('base.py', 'base.pyc', '__init__.py', '__init__.pyc'):
        continue
    try:
        exec compile('command_plugins["%s"] = commands.%s.Plugin.Command()'
                     % (plugin, plugin), '<string>', 'exec')
    except AttributeError:
        print 'Warning: failed to load command plugin "%s"' % plugin

command_history = []


def connect_to_jira():
    return Jira()


def shell():
    return raw_input('/%s > ' % '/'.join(Jira.cache.cwd[1:]))


def dispatch(command):
    args = command.split()[1:]
    command = command.split()[0]
    if command == 'help':
        help(args)
    elif command == '!':
        history()
    elif command in command_plugins.keys():
        command_plugins[command].run(connect_to_jira(), args)
    else:
        print '%s: command not found' % command


def help(command):
    if command:
        command = command[0]
    if not command:
        print 'Print help text for a specified command'
        print 'Usage: help [commands || [command_name]]'
        print 'Example:'
        print '    help commands'
        print '    help ls'
        return
    if command == 'commands':
        print 'Available commands:'
        print
        for command in command_plugins.keys():
            print command.ljust(10), ':', command_plugins[command].help
        print
        print 'For help on a specific command type: help <command>'
        return
    if command == '!':
        print 'Print command history'
        print 'Usage: ![#]'
        print 'Example:'
        print '    !'
        print '    !2'
        return
    print command_plugins[command].help
    print
    print 'Usage: %s' % command_plugins[command].usage
    if command_plugins[command].options_help:
        print 'Options:'
        print command_plugins[command].options_help
    if command_plugins[command].examples:
        print 'Examples:'
        print command_plugins[command].examples


def history():
    count = 0
    for command in command_history:
        print count, ':', command
        count += 1


def main():
    p = optparse.OptionParser()
    p.add_option('--command', '-c', action='store_true', dest='command')
    p.add_option('--shell', '-s', action='store_true', dest='shell')
    p.add_option('--web', '-w', action='store_true', dest='web')
    options, arguments = p.parse_args()
    if options.command:
        commands = arguments[0].split(';')
        for command in commands:
            arguments = command.split()
            dispatch(' '.join(arguments))
    elif options.shell:
        command = ''
        print 'Jira Shell 0.4'
        print 'Type "help" to get started. Type "quit" to exit.'
        while command != 'quit':
            command = shell()
            if command and command != 'quit':
                if command[:1] == '!':
                    args = command.split('-')[1:]
                    bang = command.split('-')[0].strip()
                    execute = []
                    if len(bang) > 1:
                        try:
                            index = int(bang[1:])
                            command = command_history[int(index)]
                            hist_args = command.split('-')[1:]
                            execute.append(command.split('-')[0].strip())
                            save_history = False
                            for harg in hist_args:
                                replaced = False
                                for arg in args:
                                    if arg[0] == harg[0]:
                                        execute.append('-' + arg.strip())
                                        replaced = True
                                        save_history = True
                                if not replaced:
                                    execute.append('-' + harg.strip())
                        except:
                            print 'Error: invalid history index'
                            continue
                        for arg in args:
                            if '-' + arg not in execute:
                                execute.append('-' + arg)
                                save_history = True
                        command = ' '.join(execute)
                        if save_history:
                            command_history.insert(0, command)
                            if len(command_history) > 10:
                                del command_history[10:]
                else:
                    command_history.insert(0, command)
                    if len(command_history) > 10:
                        del command_history[10:]
                dispatch(command)
    elif options.web:
        import BaseHTTPServer

        class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('/ > <input type="text" size="80" />')
                return

        httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 9876), Handler)
        sa = httpd.socket.getsockname()
        print 'Started server on', sa[0], 'port', sa[1], '...'
        httpd.serve_forever()


if __name__ == '__main__':
    main()
