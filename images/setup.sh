#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

docker build -t localhost:5000/basecase-basic /vagrant/bc_site/basecase/images/Dockerfile || exit 1
docker push localhost:5000/basecase-basic
docker build -t localhost:5000/spades:3.1 /vagrant/bc_site/basecase/images/assemblers/SPAdes/3.1/Dockerfile
docker push localhost:5000/spades:3.1

