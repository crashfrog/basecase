FROM localhost:5000/basecase-basic-jre
MAINTAINER Justin Payne, justin.payne@fda.hhs.gov

RUN apt-get install git ant wget bzip2 gcc g++ make default-jdk libbz2-dev zlib1g-dev ncurses-dev -y
WORKDIR /tmp/
RUN git clone https://github.com/marbl/MHAP.git
WORKDIR /tmp/MHAP/
RUN ant

WORKDIR /tmp/
RUN wget http://downloads.sourceforge.net/project/wgs-assembler/wgs-assembler/wgs-8.2beta/wgs-8.2beta.tar.bz2 -q
RUN bzip2 -dc /tmp/wgs-8.2beta.tar.bz2 | tar -xf -
WORKDIR /tmp/wgs-8.2beta/kmer
RUN make install
WORKDIR /tmp/wgs-8.2beta/samtools
RUN make
WORKDIR /tmp/wgs-8.2beta/src
RUN make

WORKDIR /data/
ADD http://www.cbcb.umd.edu/software/PBcR/MHAP/asm/pacbio.spec /data/

RUN apt-get remove ant gcc g++ make bzip2 git -y
RUN apt-get clean
RUN apt-get autoclean

