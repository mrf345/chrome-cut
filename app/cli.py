# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from .core import *
from sys import exit


def cli():
    mhelp = "--help :\n\t Usage:\n\t %s --help\n\t # to print this message" % (
        argv[0])
    mhelp += "\n--list_network:\n\t # to list available networks with index\n"
    mhelp += "\n\t %s --check [ip] \n\t # check if ip is chrome cast \n" % (
        argv[0])
    mhelp += "\n\t %s --scan \n\t # to scan your network " % (argv[0])
    mhelp += "for active chrome casts \n\n"
    mhelp += "\t %s --scan_verbose \n\t # -scan with full details \n\n" % (
        argv[0])
    mhelp += "\t %s --reset [IP] \n\t # system reset a chrome cast \n\n" % (
        argv[0])
    mhelp += "\t %s --shut [IP] \n\t # to keep shuting selected chrome " % (
        argv[0])
    mhelp += "cast for a set duration \n\n"
    mhelp += "\t %s --shut_auto \n\t # -shut with auto detection \n" % (
        argv[0])
    mhelp += "\n\t %s --cast [ip] \n\t # keep casting a video\n" % (argv[0])
    margv = []
    for args in argv:
        margv.append(args)
    if len(margv) < 1:
        print(mhelp)
        exit(0)
    margv.append(" ")
    if margv[1] == '--help':
        print(mhelp)
    elif margv[1] == '--scan' or margv[1] == '--scan_verbose':
        rip = ch_ip()
        if argv[1] == '--scan_verbose':
            cc = loop_ips(rip, vbos=True)
        else:
            cc = loop_ips(rip)
        if cc is None:
            print("Error : no chromecast devices were found ..")
            exit(0)
        else:
            print("$" * 5, " List of chrome cast found ", "$" * 5)
        for c in cc:
            print(" >>> " + c)
    elif margv[1] == '--check':
        margv.append(" ")
        if len(argv) < 3:
            print(mhelp)
            exit(0)
        print("?" * 4, " Checking the inputed ip ..")
        if not det_ccast(str(argv[2]))[0]:
            print(mhelp)
            print(
                "\n Error: whatever you have inputed is not a chrome cast ..")
            exit(0)
        else:
            print("^" * 3, str(argv[2]) + " that is a chrome cast ..")
    elif margv[1] == '--reset':
        margv.append(" ")
        if len(argv) < 3:
            print(mhelp)
            exit(0)
        print("?" * 4, " Checking the inputed ip ..")
        if not det_ccast(str(argv[2]))[0]:
            print(mhelp)
            print(
                "\n Error: whatever you have inputed is not a chrome cast ..")
            exit(0)
        if reset_cc(str(argv[2])):
            print(">" * 3, str(argv[2]) + " has been successfully reseted ..")
        else:
            print("^" * 3, str(argv[2]) + " failed to reset ..")
    elif margv[1] == '--shut':
        margv.append(" ")
        if len(argv) < 3:
            print(mhelp)
        else:
            print("?" * 4, " Checking the inputed ip ..")
            if not det_ccast(str(margv[2]))[0]:
                print(mhelp)
                nmsg = "\n Error: whatever you have inputed"
                nmsg += " is not a chrome cast .."
                exit(0)
            shut(dip=str(argv[2]), auto=False)
    elif margv[1] == '--shut_auto':
        shut()
    elif margv[1] == '--cast':
        margv.append(" ")
        if len(argv) < 3:
            print(mhelp)
        else:
            print("?" * 4, " Checking the inputed ip ..")
            if not det_ccast(str(margv[2]))[0]:
                print(mhelp)
                nmsg = "\n Error: whatever you have inputed"
                nmsg += " is not a chrome cast .."
                exit(0)
            cast(dip=str(argv[2]))
    else:
        print(mhelp)
    exit(0)
