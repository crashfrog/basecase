FROM localhost:5000/basecase-basic:latest
MAINTAINER Justin Payne, justin.payne@fda.hhs.gov

RUN apt-get install g++ make git cmake autoconf bzip2 build-essential -y

#sparsehash
WORKDIR /tmp/
ADD https://sparsehash.googlecode.com/files/sparsehash_2.0.2-1_amd64.deb /tmp/
RUN dpkg -i /tmp/sparsehash_2.0.2-1_amd64.deb

#zlib
RUN apt-get install -y zlibc zlib1g zlib1g-dev

#samtools
RUN git clone https://github.com/pezmaster31/bamtools.git
WORKDIR /tmp/bamtools/build
RUN cmake ..
RUN make

#jemalloc
WORKDIR /tmp/
RUN wget http://www.canonware.com/download/jemalloc/jemalloc-3.6.0.tar.bz2
RUN tar -xjf jemalloc-3.6.0.tar.bz2

#SGA
WORKDIR /tmp/
RUN git clone https://github.com/jts/sga.git
WORKDIR /tmp/sga/src/
RUN ./autogen.sh
RUN ./configure --with-jemalloc=/tmp/jemalloc-3.6.0/lib/ --with-bamtools=/tmp/bamtools/

RUN apt-get remove cmake bzip2 git g++ gcc make -y
RUN apt-get clean
RUN apt-get autoclean