#  nmap3.py
#
#  Copyright 2019 Wangolo Joel <wangolo@ldap.testlumiotic.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import shlex
import subprocess
import sys
import os
import ctypes
import functools
from nmap3.exceptions import NmapNotInstalledError

__author__ = 'Wangolo Joel (inquiry@nmapper.com)'
__version__ = '1.9.3'
__last_modification__ = 'Jun/06/2025'

def get_nmap_path(path:str='') -> str: 
    """
    Accepts path, validate it. If not valide, search nmap path
    Returns the location path where nmap is installed
    by calling which nmap
    If not found raises NmapNotInstalledError
    """
    if path and (os.path.exists(path)):
        return path

    os_type = sys.platform
    if os_type == 'win32':
        cmd = "where nmap"
    else:
        cmd = "which nmap"
    args = shlex.split(cmd)
    sub_proc = subprocess.Popen(args, stdout=subprocess.PIPE)

    output, e = sub_proc.communicate(timeout=15)
    if e:
        print(e)

    if not output:
        raise NmapNotInstalledError(path=path)
    if os_type == 'win32':
        return output.decode('utf8').strip().replace("\\", "/")
    return output.decode('utf8').strip()

def get_nmap_version():
    nmap = get_nmap_path()
    cmd = nmap + " --version"

    args = shlex.split(cmd)
    sub_proc = subprocess.Popen(args, stdout=subprocess.PIPE)

    try:
        output, _ = sub_proc.communicate(timeout=15)
    except Exception as e:
        print(e)
        sub_proc.kill()
    else:
        return output.decode('utf8').strip()

def user_is_root(func):
    def wrapper(*args, **kwargs):
        try:
            is_root_or_admin = (os.getuid() == 0)
        except AttributeError:
            is_root_or_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            
        if(is_root_or_admin):
            return func(*args, **kwargs)
        else:
            return {"error":True, "msg":"You must be root/administrator to continue!"}
    return wrapper 

def nmap_is_installed_async():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            nmap_path = get_nmap_path()
                
            if(os.path.exists(nmap_path)):
                return await func(*args, **kwargs)
            else:
                print({"error":True, "msg":"Nmap has not been install on this system yet!"})
                return {"error":True, "msg":"Nmap has not been install on this system yet!"}
        return wrapped
    return  wrapper 
