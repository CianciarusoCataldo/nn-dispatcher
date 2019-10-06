#!/usr/bin/env python
"""
MIT License
Copyright (c) 2016 Paul Kramme
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Author: Cianciaruso Cataldo
"""

from flask import Flask, request, send_from_directory
import os
import sys
import configparser
import requests
from flask_optimizer import Compress
from threading import Thread

"""Root directory of the app"""
execution_path=os.getcwd()


"""
List of all available servers. It's used to reach the right url. If you wish to
manage more servers, add them to "servers_list.txt" file, in the root directory,
with a dedicated name, one for row:

server1 <server url>
server2 <server url>
...

Remember that the name of the server will be also the default return message
if there is a problem during connection. If you don't specify a server list,
a default value will be used.
"""
servers={}
parser = configparser.ConfigParser()
    
parser.read(os.path.join(os.getcwd(),'config.ini'))
server_list=parser["SERVERS"]
print("\nReading custom server list..\n")

for server in server_list:
    try:
        request = requests.get(parser["SERVERS"][server])
        if request.status_code == 200:
            servers[server]=parser["SERVERS"][server]
            print("Server online : "+str(server)+" - "+str(servers[server])+"\n")

        else:
            print(str(parser["SERVERS"][server])+" is not a valid url. Skipping..\n")
    except:
        print(str(parser["SERVERS"][server])+" is not a valid url. Skipping..\n")
 
if len(servers)<1:
    print("\nServer list is empty, please add your server to config.ini file")
    sys.exit(0)
        
class Server_Thread(Thread):
    """
    Custom Thread class, used to handle requests in asyncronous way.
    If your server list became too large, it's better to use 'requests-future'
    """

    def __init__(self, file, header, key):
        """
        Create a custom Thread, to handle requests.

        :param file: file to send to server
        :param header: custom header for the request(can be empty)
        :type header: dict
        :param key: server name
        :type key: str
        """
        self._server_name=key
        if (key not in servers):
            """
            Define a custom thread to send request to server.

            :params 
            """
            print("\nServer_Thread Error -> Invalid server name :"+str(key)+
                  ". No request will be send")
            self._invalid_server=True

        else:
            self._invalid_server=False
            self._return_value=""
            self._file=file
            self._header=header
            self._server_name=key

        super(Server_Thread, self).__init__()


    def run(self):
        if(self._invalid_server):
            self._return_value=self._server_name
        else:
            res=receive_result(self._server_name, self._file, self._header)
            self._return_value=res
        
    def get_value(self):
        return self._return_value

"""
Create a Flask app and then apply optimizations, like gzip compression and
caching policy
"""
app = Flask(__name__)
Compress(app)

#Handle requests to web server, using Flask micro-framework.
#You can put your custom website into "static" folder,
#and it will be shown if a user reach server url using browser.

@app.route('/js/<string>')
def send_js(string):
    """
    Handle javascript module request from client.

    :param string: javascript module name
    :type string: str
    :returns: javascript file path
    :rtype: str
    """
    return send_from_directory(os.path.join(os.path.join(execution_path,'static'),'js'), string)

@app.route('/img/<string>')
def send_img(string):
    """
    Handle image request from client.

    :param string: image file name
    :type string: str
    :returns: image file path
    :rtype: str
    """
    return send_from_directory(os.path.join(os.path.join(execution_path,'static'),'img'), string)

@app.route('/css/<string>')
def send_css(string):
    """
    Handle css file request from client.

    :param string: css file name
    :type string: str
    :returns: css file path
    :rtype: str
    """
    return send_from_directory(os.path.join(os.path.join(execution_path,'static'),'css'), string)


@app.route('/fonts/<string>')
def send_fonts(string):
    """
    Handle font file request from client.

    :param string: font file name
    :type string: str
    :returns: font file path
    :rtype: str
    """
    return send_from_directory(os.path.join(os.path.join(execution_path,'static'),'fonts'), string)


@app.route('/favicon.ico')
def send_ico():
    """
    Handle icon file request from client.
    :returns: icon file path
    :rtype: str
    """
    return app.send_static_file('favicon.ico')


@app.route('/',methods = ['GET'])
def root():
    """
    Handle index file request from client.

    :returns: index file path
    :rtype: str
    """
    return app.send_static_file('index.html')



@app.route('/<path:path>',methods = ['GET'])
def error(path):
    """
    Handle eventual internal error. You can optionally use your custom error
    page, just add it to 'static' folder and return it with
    'app.send_static_file' method.

    :param path: file path
    """
    if not(os.path.isfile(path)):
        return "Application error : "+path+" not exists."



#Delete this rule if you want to handle other paths for POST request
#in your website
@app.route('/<path>',methods = ['POST'])
def invalid_request(path):
    return "Invalid request form : "+path


@app.route('/',methods = ['POST'])
def check_req():
    """
    Handle POST request. The user can choose a specific server to connect by
    insert a custom header ("mode") in the message, containing server name.
    Note that this name must be in "servers", otherwise no request will be sent.
    """
    if "mode" in request.headers:
        post_req_custom(request.headers["mode"])
    else:
        return post_req_all()
              

def post_req_all(header={}):
    """
    Send a post request(async), containing the image to analyze, to all the
    servers into "servers" list, and return the response, as a string.

    :param header: optional custom header, if specified it will be used
    :returns: response from the server(s)
    :rtype: str
    """
    file = {'image': (request.files['image'].read())}
    thread_list=[]
    response=""
    
    for server in servers:
        thread_req=Server_Thread(file, header, server)
        thread_list.append(thread_req)
        thread_req.start()

    for sthread in thread_list:
        sthread.join()

    for sthread in thread_list:
        response+=sthread.get_value()
        
    return response


def post_req_custom(server, header={}):
    """
    Send a post request(async), containing the image to analyze, to the
    specified server. The server must be into "servers" list, otherwise no
    request will be send. Finally, return the response, as a string.

    :param server: server name to send request to (must be into "servers" list)
    :param header: optional custom header, if specified it will be used
    :returns: response from the server(s)
    :rtype: str
    """
    file = {'image': (request.files['image'].read())}
    thread_req=Server_Thread(file, header, server)
    thread_req.start()
    thread_req.join()
    response=thread_req.get_value()
    return response



def receive_result(server_name, file, header={}):
    """
    Send a post request to specified server, containing a file and a custom header,
    then return response as string.

    :param server_name: server to send request to (must be into "servers" list)
    :param file: file that will be sent to server
    :param header: optional custom header, if specified it will be used
    :returns: response from server as a string
    :rtype: str
    """
    result=""
    try:
        r=requests.post(servers[server_name], files=file, headers=header)
        result=r.text
    except requests.exceptions.RequestException:
        result=server_name
    return result


#Use a webserver to run, like Gunicorn or Waitress    
if __name__ == "__main__":
    pass
