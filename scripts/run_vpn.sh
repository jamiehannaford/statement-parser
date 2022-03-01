#!/bin/bash

bash /tmp/entrypoint.sh

file="/tmp/valid-ip"
while true; do 
    ip=$(curl -s icanhazip.com)
    if [ "$ip" == "$HOME_IP" ]; then
        [ -f $file ] && rm $file
    else
        touch $file
    fi
    sleep 5
done
