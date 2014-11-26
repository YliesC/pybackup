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
import ConfigParser

from pprint import pprint

CONFIG_FILE=".backup"

username = os.getlogin()
uid = os.getuid()
gid = os.getgid()
backup_dir_location='%s/backup' % os.getenv('HOME')

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

    # Verbose
    parser.add_argument(
                "-v", "--verbose", action='store_true', default=False,
                help="slightly more verbose during backup" )

    # Upload tarball on FTP server
    parser.add_argument('--ftp', '-f', action='store_true', default=False,
                        help="upload your backup on an ftp server and keep a local version")

    return parser

def filter_function(tarinfo):
    """ Filter to exclude some dir/file from backup """
    try:
        excludes = config.items("excludes")
    except:
        print "NoSectionError: error in your config files, please check if section 'excludes' exist in [%s] config file" % CONFIG_FILE
        sys.exit(0)

    for key, path in excludes:
        if fnmatch.fnmatch(tarinfo.name, path):
            verboseprint(bcolors.FAIL, '[Excluded]', bcolors.WARNING, tarinfo.name, bcolors.ENDC)
            return None
    else:
        verboseprint(bcolors.OKGREEN, '[Ok]      ', bcolors.OKBLUE, tarinfo.name, bcolors.ENDC)
        return tarinfo

def is_dir_ok():
    """ Check if backup dir is ready """

    if not os.path.exists(backup_dir_location):
        try:
            os.mkdir(backup_dir_location)
        except OSError, err:
            raise err


def touch(path):
    """ Small fucntion to create an empty file """

    with open(path, 'a'):
        os.utime(path, None)

def main():
    """ main """

    print "%s Start backing your files bro! %s" %(bcolors.HEADER, bcolors.ENDC)
    timestamp = datetime.datetime.now().strftime('%d-%b-%Hh-%Mm-%G')
    pc_name = os.uname()[1]
    # Path to the created tar file ( change as you want )
    tar_name = '%s/backup/%s-backup-%s.tar.gz' % (os.getenv('HOME'), pc_name, timestamp)

    is_dir_ok()

    try:
        includes = config.items("includes")
    except:
        print "NoSectionError: error in your config files, please check if section 'includes' exist in [%s] config file" % CONFIG_FILE
        sys.exit(0)

    liste = list()
    for key, path in includes:
        liste.append(path)

    try:
        tar = tarfile.open(tar_name, 'w:gz')
        print "Backing ..."

        for obj in liste:
            verboseprint("-------------------------")
            verboseprint("| Adding ", obj.strip("\n"), " directory/file to backup")
            verboseprint("-------------------------")
            tar.add(obj.strip("\n"), filter=filter_function)
        tar.close()
    except tarfile.TarError, tarexc:
        raise tarexc

    if options.ftp:
        print ftp.storbinary("STOR " + os.path.basename(tar_name), open(tar_name)) # Send the file
        ftp.quit()
        print "Your file [%s] was uploaded succefully on %s!" % (tar_name, config.get("ftp", "server_address"))

    print "Your backup archive is ready!"
    print "You can find it at: [%r]" % tar_name

if __name__ == '__main__':
    args = sys.argv[1:]
    parser = mk_parser()
    options = parser.parse_args(args)

    config = ConfigParser.RawConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        touch(CONFIG_FILE)

    if options.verbose:
        # Verbose function:  add/remove thing to do when -v option is set
        def verboseprint(*args):
            for arg in args:
                print arg,
            print
    else:
        verboseprint = lambda *a: None      # do-nothing function

    if options.ftp:
        import ftplib

        ftp = ftplib.FTP()
        print ftp.connect(config.get("ftp", "server_address"), 21)
        try:
            print "Logging in..."
            print ftp.login(config.get("ftp", "username"), config.get("ftp", "password"))
            print ftp.cwd(config.get("ftp", "upload_dir"))
        except:
            print "503: Inccorect login."
            sys.exit(0)

    main()
