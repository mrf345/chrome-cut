# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import socket
from netifaces import ifaddresses, interfaces
from sys import exit, argv
from os import system, name
import asyncio
from requests import post, delete, get
from json import dumps
from time import sleep
import click

counter = 0  # global counter to count tasks, too tired to think of any better
ports = [8008, 8009]  # global chrome cast known ports


def get_ips(gui=False):
    """ Getting a list of ips obtained by all network interfaces """
    list_of_ips = []
    for interface_name in interfaces():
        try:
            list_of_ips.append('%s%s' % (
                ('' if name == 'nt' or not gui else interface_name + ' , '),
                ifaddresses(interface_name)[2][0].get('addr')))
            # getting a string of the interface name and its obtained ip
        except:
            pass
    if len(list_of_ips) >= 1:
        return list_of_ips
    return None


def is_ccast(ip, timeout=0.1):
    """ to check without async, if ip is legit chrome cast device """
    global ports
    results = []
    for port in ports:
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            for i in get_ips():  # getting the network card ip to connect with
                if '.'.join(ip.split('.')[0:-1]) in i:
                    connected_ip = i
            socket.setdefaulttimeout(timeout)
            socket_obj.bind((connected_ip, 0))
            result = socket_obj.connect_ex((ip, port))
            results.append(result)
        except:
            pass
        socket_obj.close()
    return True if 0 in results else False


@asyncio.coroutine
# old style since using py3.4 to insure compatibility between CC-gui CC-cli
def det_ccast(ip, log=False, timeout=0.05):
    """
    to detect chrome cast with its known ports and return its ip
    and status in list, asyncrnioudfdslfr-sly.
    """
    global ports
    results = []  # in-which socket response will be stored to check later
    for port in ports:
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for i in get_ips():  # getting the network card ip to connect with
            if '.'.join(ip.split('.')[0:-1]) in i:  # cutting of the last digit
                connected_ip = i
        socket.setdefaulttimeout(timeout)
        try:
            socket_obj.bind((connected_ip, 0))
            result = socket_obj.connect_ex((ip, port))
            results.append(result)
        except:
            pass
        socket_obj.close()
    if log:
        global counter
        counter += 1
        click.clear()
        click.echo(
            click.style(
                'Completed : ' + str(int(counter * 100 / 255)) + '%',
                bold=True, fg='red'))
        click.echo()
        click.echo(
            click.style(
                ' == ' + ip,
                blink=False, bg='red', fg='black'))
        click.echo(
            click.style(
                ('[' + '=' * int(counter / 10)) + ']',
                blink=False, bg='red', fg='black'))
        click.clear()
    yield from asyncio.sleep(0)
    return [True, ip] if 0 in results else [False, ip]


def loop_ips(ip, log=False, timeout=0.05):
    """ looping through the ips from ch_ip till 255 and detect using
    det_ccast and returning a list of potential chromecasts """
    active_ccasts = []  # detected chrome casts stored here
    loop = asyncio.get_event_loop()
    tasks = [det_ccast(  # fetching the range of ips to async function
        '.'.join(ip.split('.')[0:-1]) + '.' + str(i),
        log, timeout) for i in range(1, 256)]
    results = loop.run_until_complete(asyncio.gather(asyncio.wait(tasks)))
    #  loop.close() should be stopped in the before exist
    #  FIXME: register loop.close() to before exit
    for result in results[0][0]:  # looking for successful ones
        global counter
        counter = 0  # clearing up the global counter
        if result.result()[0]:
            active_ccasts.append(result.result()[1])
    return active_ccasts if len(active_ccasts) >= 1 else None


def reset_cc(ip):
    """ sending json a request to system restore """
    global ports
    for port in ports:
        try:
            post(
                "http://" + ip + ":" + str(port) + "/setup/reboot",
                data=dumps({"params": "fdr"}),
                headers={'Content-type': 'application/json'})
            return True
        except:
            pass
    return False


def cancel_app(ip):
    """ canceling whatever been played on chrome cast """
    global ports
    for port in ports:
        try:
            delete(
                "http://" + ip + ":" + str(port) + "/apps/YouTube",
                headers={'Content-type': 'application/json'})
            return True
        except:
            pass
    return False


def send_app(ip, video_link="v=04F4xlWSFh0&t=9"):
    """ stream youtube video to chrome cast """
    global ports
    for port in ports:
        try:
            post("http://" + ip + ":" + str(port) + "/apps/YouTube",
                 data=video_link,
                 headers={'Content-type': 'application/json'})
            return True
        except:
            pass
    return False


def cast(ip='192.168.0.188', video=False, duration=1,
         log=False, counter=1):
    """ recurrence casting a video to inserted ip forever """
    if duration <= 0:
        raise AttributeError("Error: too small of a duration, greater than 0")
    click.clear() if log else None
    if is_ccast(ip):
        send_app(ip, video) if video else send_app(ip)
        if log:
            click.echo(
                click.style(
                    'Success: streamed to ' + ip,
                    bold=True, fg='blue'))
            click.echo()
    else:
        raise AttributeError("Error: requires an active chrome cast IP")
    if log:
        click.echo(
            click.style(
                "[" + "Number of streams done : " + str(counter) + "]",
                blink=False, bg='red', fg='black'))
        click.echo("\n")
        click.echo(click.style("< # > Ctrl-c to exit",
                               fg='green'))
        click.clear()
    sleep(duration)
    return cast(ip, video, duration, log, counter + 1)


def block(ip='192.168.0.188', duration=1, log=False, counter=1):
    """ recurrence stream abort inserted ip forever """
    if duration <= 0:
        raise AttributeError("Error: too small of a duration, greater than 0")
    click.clear() if log else None
    if is_ccast(ip):
        cancel_app(ip)
        if log:
            click.echo(
                click.style(
                    'Success: stream aborted on ' + ip,
                    bold=True, fg='blue'))
            click.echo()
    else:
        raise AttributeError("Error: requires an active chrome cast IP")
    if log:
        click.echo(
            click.style(
                "[" + "Number of stream aborts : " + str(counter) + "]",
                blink=False, bg='red', fg='black'))
        click.echo("\n")
        click.echo(click.style("< # > Ctrl-c to exit",
                               fg='green'))
        click.clear()
    sleep(duration)
    return block(ip, duration, log, counter + 1)


def shut(ip='192.168.0.188', duration=1,
         log=False, counter=1):
    """ recurrence factory reseting inserted ip forever """
    if duration <= 0:
        raise AttributeError("Error: too small of a duration, greater than 0")
    click.clear() if log else None
    if is_ccast(ip):
        reset_cc(ip)
        if log:
            click.echo(
                click.style(
                    'Success: factory reset to ' + ip,
                    bold=True, fg='blue'))
            click.echo()
    else:
        raise AttributeError("Error: requires an active chrome cast IP")
    if log:
        click.echo(
            click.style(
                "[" + "Number of factory resets done : " + str(counter) + "]",
                blink=False, bg='red', fg='black'))
        click.echo("\n")
        click.echo(click.style("< # > Ctrl-c to exit",
                               fg='green'))
        click.clear()
    sleep(duration)
    return shut(ip, duration, log, counter + 1)
