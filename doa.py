#!/usr/bin/env python3

################################################################################
### NZBGET API SCRIPT                                                        ###
################################################################################

# Web Dyno DoA Decider script by ssnjr for heroku.
#
# Checks if server is in standby or not, and pings if it isn't in standby.
#
# Server is in standby when there are no downloads in progress (server paused 
# or all jobs completed).
#
# A web dyno sleeps if it doesn't receive any traffic within 30 mins so the 
# script pings every 29 minutes when the server is not in standby to prevent 
# nzbget from dying during an ongoing process.
#
# To save dyno hours the script doesn't ping when server is in standby i.e. 
# when it is not in use.
#
# The script can keep an instance alive for 24 hrs.

################################################################################
### NZBGET API SCRIPT                                                        ###
################################################################################

import os
import re
import sys
import requests
from sys import argv
from xmlrpc.client import ServerProxy

task = argv[1]

host = '127.0.0.1'
port = os.environ.get('PORT')
username = os.environ.get('CTRL_USERNAME')
password = os.environ.get('CTRL_PASS')
app_url = os.environ.get('APP_URL')

# Build an URL for XML-RPC requests
rpcUrl = f'http://{username}:{password}@{host}:{port}/xmlrpc'
server = ServerProxy(rpcUrl)  # Create remote server object

# task_list = [
#   'ping', 'return_bool', 'return_file_path', 'set_false', 'set_true']
def ping(task):

    if task != 'ping':
        file_root = '/home/'
        ping_true_path = file_root + 'ping.true'
        ping_false_path = file_root + 'ping.false'

        for dir in os.listdir(file_root):
            if re.search(r'^ping', dir):

                if task == 'return_file_path':
                    return file_root + dir
                elif task == 'return_bool':
                    return eval(
                        dir.split('.')[1].capitalize())
                elif task == 'set_false':
                    os.rename(
                        ping('return_file_path'), ping_false_path)
                elif task == 'set_true':
                    os.rename(
                        ping('return_file_path'), ping_true_path)

    elif task == 'ping':
        try:
            response = requests.get(app_url)
            response_time = int(response.elapsed.total_seconds()*1000)
            message = f'PING: {response.url} - ' + \
                      f'pinged sucessfully ({response_time}ms)'
            server.writelog('INFO', message)
        except:
            message = f'Can\'t ping "{app_url}" please ensure the app url ' + \
                       'is entered in correctly'
            server.writelog('ERROR', message)

if task == 'ping_check':
    # Fetches bool Status for the following:
    ServerStandBy = server.status()['ServerStandBy']
    DownloadPaused = server.status()['DownloadPaused']

    # Pings the server if server is not in standby or if download is paused:
    if not ServerStandBy or DownloadPaused:
        ping('ping'); ping('set_true')

    # Opposite of the above condition:
    elif ServerStandBy and not DownloadPaused:
        ping('set_false')

elif task == 'shutdown':
    server.shutdown()

sys.exit(0)
