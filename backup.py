#!/usr/bin/env python

# #############################################################################
#
# Name : backup.py
"""
 Summary : Backup specified files using tar command

"""
# #############################################################################

__author__    = "chahi_y"
__email__     = "ylies.chahi@epitech.eu"

import sys
import datetime
import os
import tarfile
import argparse
import fnmatch

from pprint import pprint

username = os.getlogin()
uid = os.getuid()
gid = os.getgid()
HOME_PATH='home/%s' % username

# Add elem as the example
obj_to_exclude = [
    "%s/backup" % HOME_PATH,
]

# Add elem as the example
obj_to_include = [
    "/home/%s" % username
]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def mk_parser():
    """ generates command line parser """

    parser = argparse.ArgumentParser(
                    description="Backup your files and store it using tar command")

    parser.add_argument(
                "-v", "--verbose", action='store_true', default=False,
                help="slightly more verbose during backup" )

    return parser

def filter_function(tarinfo):
    """ Filter to exclude some dir/file from backup """

    for obj in obj_to_exclude:
        if fnmatch.fnmatch(tarinfo.name, obj):
            verboseprint(bcolors.FAIL, '[Excluded]', bcolors.WARNING, tarinfo.name, bcolors.ENDC)
            return None
    else:
        verboseprint(bcolors.OKGREEN, '[Ok]      ', bcolors.OKBLUE, tarinfo.name, bcolors.ENDC)
        return tarinfo

def is_dir_ok():
    """ Check if backup dir is ready """

    if not os.path.exists("backup"):
        try:
            os.mkdir("backup")
        except OSError, err:
            raise err

def main():
    """ main """

    print "Start backing your files bro!"
    timestamp = datetime.datetime.now().strftime('%d-%b-%Hh-%Mm-%G')
    pc_name = os.uname()[1]
    # Path to the created tar file ( change as you want )
    tar_name = '/home/%s/backup/pc-backup-%s.tar.gz' % (username, timestamp)

    is_dir_ok()

    try:
        tar = tarfile.open(tar_name, 'w:gz')
        print "Backing ..."
        for obj in obj_to_include:
            verboseprint("-------------------------")
            verboseprint("| Adding ", obj, " folder to backup")
            verboseprint("-------------------------")
            tar.add(obj, filter=filter_function)
        tar.close()
    except tarfile.TarError, tarexc:
        print tarexc

    print "Your backup archive is ready!"
    print "You can find it at: [%r]" % tar_name

if __name__ == '__main__':
    args = sys.argv[1:]
    parser = mk_parser()
    options = parser.parse_args(args)

    if options.verbose:
        # Verbose function:  add/remove thing to do when -v option is set
        def verboseprint(*args):
            for arg in args:
                print arg,
            print
    else:
        verboseprint = lambda *a: None      # do-nothing function
    main()
