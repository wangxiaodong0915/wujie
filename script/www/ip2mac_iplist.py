__author__ = 'lenovo'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = InBi
# datetime = 2017-06-13 23:19
# 发现网络地址冲突。根据IP地址判断MAC地址的变化情况。

import os
import platform
import re
import datetime

class IP2MAC:
    def __init__(self):
        self.patt_mac = re.compile('([a-f0-9]{2}[-:]){5}[a-f0-9]{2}', re.I)

    def getMac(self, ip):
        sysstr = platform.system()
        if sysstr == 'Windows':
            macaddr = self.__forWin(ip)
        elif sysstr == 'Linux':
            macaddr = self.__forLinux(ip)
        else:
            macaddr = None
        return macaddr or '00-00-00-00-00-00'

    def __forWin(self, ip):
        os.popen('ping -n 1 -w 500 {} > nul'.format(ip))
        macaddr = os.popen('arp -a {}'.format(ip))
        macaddr = self.patt_mac.search(macaddr.read())
        if macaddr:
            macaddr = macaddr.group()
        else:
            macaddr = None
        return macaddr

    def __forLinux(self, ip):
        os.popen('ping -nq -c 1 -W 500 {} > /dev/null'.format(ip))
        result = os.popen('arp -an {}'.format(ip))
        result = self.patt_mac.search(result.read())
        return result.group() if result else None

if __name__ =='__main__':
    g = IP2MAC()
    iplist = ('10.120.131.234'
              ,'10.120.131.235'
              ,'10.120.131.236'
              ,'10.120.131.237'
              ,'10.120.131.243'
              ,'10.120.131.244'
              ,'10.120.131.245'
              ,'10.120.131.246'
              ,'10.120.131.247'
              ,'10.120.131.248'
              ,'10.120.131.249'
            )
    mac_a = {ip:'' for ip in iplist}
    mac_b = {ip:'' for ip in iplist}
    while True:
        for ip in iplist:
            mac_a[ip] = g.getMac(ip)
            if mac_b[ip] == "":
                mac_b[ip] = mac_a[ip]
            elif mac_a[ip] == mac_b[ip] and mac_b[ip] != "":
                pass
            else:
                index= index + 1
                print(ip,'---变化前',mac_b[ip],'---变化后',mac_a[ip],'--发现时间：',datetime.datetime.now())
                mac_b[ip] = mac_a[ip]