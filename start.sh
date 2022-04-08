#!/bin/sh
while [ 1 ] ; do python main.py & prid=$! && echo $prid ; sleep 600 && kill $prid ; done
