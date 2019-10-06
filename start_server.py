import configparser
import os
import subprocess
import sys

config_path=os.path.join(os.getcwd(),'config.ini')
print("\nStarting dispatching server..")

if not(os.path.isfile(config_path)):
    f=open(config_path,'a')
    f.write("[SERVERS]\n")
    f.write("#Add here your custom servers, where you want to dispatch the request, with the pattern:\n#<server_name>=<server_ip>")
    f.write("\n\n[NETWORK]")
    f.write("\n#Add here the webserver port (default value 8080)\n")
    f.write("\nport=8080\n")
    f.close()
    print("Missing config.ini file, it will be generated with default value.")

parser=configparser.ConfigParser()
parser.read(config_path)

if not "NETWORK" in parser.sections():
    f=open(config_path,'a')
    f.write("\n[NETWORK]")
    f.write("\nport=8080\n")
    f.close()
    print("\nNo port specified in config.ini file, it will be used the default value (8080)\n")
    
port=parser["NETWORK"]["port"]


subprocess.call('waitress-serve --listen=0.0.0.0:'+port+' nn_server:app', shell=True)
