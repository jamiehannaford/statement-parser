#!/bin/bash

WORKERS=$(ls config/k8s/jobs/workers | shuf -n 5)

echo ${WORKERS} > .workers 

for worker in ${WORKERS}; do 
    kubectl apply -f config/k8s/jobs/workers/$worker
done