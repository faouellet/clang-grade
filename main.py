import argparse
import os
import subprocess
import re
import yaml

import pdb

type_to_clang_check = { 
        'IfAssign' : 'clang-diagnostic-parentheses', 
        'SwitchBool' : 'clang-diagnostic-switch-bool'
        }

class Error:
    def __init__(self, type, cost):
        self.type = type
        self.cost = cost
        self.check = type_to_clang_check[self.type]

def parse_config(config):
    errors = []
    conf = open(config)
    data = yaml.safe_load(conf)
    conf.close()
    for d in data:
        errors.append(Error(d['error']['type'], d['error']['cost']))

    return errors

def init_parser():
    parser = argparse.ArgumentParser(description="CorrectUS options:")
    parser.add_argument('-dir=', dest='dir', metavar='directory', 
                        help="""Specifies the top level directory containing the assignments to grade. 
                                When the value is empty it will assume the current directory is the one containing the assignment""")
    #TODO: Add argument for outputting to file or stdout
    parser.add_argument('-config=', dest='config', metavar='config file', 
                        help="Specifies the configuration file in YAML format. When the value is empty it will use the default configuration file provided.")

    return parser

def format_command(config):
    command = "clang-tidy -checks=-*,"
    checks = [x.check for x in config]
    command = command + ','.join(checks)

    print command
    return command

def main():
    parser = init_parser()
    args = parser.parse_args()
    directory = args.dir

    marking_scheme = parse_config(args.config)
    print marking_scheme

    command = format_command(marking_scheme)

    if os.path.isdir(directory):
        for f in os.listdir(directory):
            extension = os.path.splitext(f)[1][1:]
            if extension in ["cpp", "h"]:
                p = subprocess.Popen(command.format(directory + f).split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = p.communicate()[0]
                osplit = output.split('\n')
                for line in osplit:
                    if "warning:" in line:
                        infos = line.split(':')
                        print "Mistake:{0}".format(re.sub("\[[a-zA-Z\.\-]+\]",'', infos[4]))
                        print "File: {0}, Line {1}, Column {2}".format(os.path.basename(infos[0]), infos[1], infos[2])
                        print ""
    else:
        print "Not a valid directory path"

if __name__ == '__main__':
    main()

