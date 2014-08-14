FROM localhost:5000/spades:3.1
MAINTAINER Justin Payne, justin.payne@fda.hhs.gov

#COPY CFSAN001656_S8_L001_R1_001.fastq /data/
#COPY CFSAN001656_S8_L001_R2_001.fastq /data/

RUN apt-get clean
RUN apt-get autoclean

WORKDIR /data/
CMD spades.py --test -o /tmp/