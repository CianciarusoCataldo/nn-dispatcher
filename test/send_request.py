#!/usr/bin/env python
#Author: Cianciaruso Cataldo

import requests
import os
import sys
import time


def run(image_path):
    header={'modes':'all'}
    files = {'image': ('test.jpg', open(image_path, 'rb'), 'image/jpg')}
    start_time = time.time()
    r=requests.post("http://localhost:8080", files=files, headers=header)
    print("Response :\n")
    print(r.text)
    elapsed_time = str(time.time() - start_time)
    print("\nElapsed time: "+elapsed_time)


if __name__ == "__main__":
    if(len(sys.argv)>1):
        if os.path.isfile(sys.argv[1]):
            run(sys.argv[1])
        else:
            print("Error, the file "+sys.argv[1]+" is not a valid image file.")
    else:
        print("You must specify an image file path to send request to server.")
