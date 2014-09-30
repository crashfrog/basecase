FROM localhost:5000/basecase-basic
MAINTAINER Justin Payne, justin.payne@fda.hhs.gov

WORKDIR /db/
RUN wget http://ccb.jhu.edu/software/kraken/dl/minikraken.tgz 
WORKDIR /tmp/
ADD http://ccb.jhu.edu/software/kraken/dl/kraken-0.10.4-beta.tgz /tmp/
RUN tar -xvzf kraken-0.10.4-beta.tgz
WORKDIR kraken-0.10.4-beta
