FROM crashfrog/basecase:latest
MAINTAINER Justin Payne, justin.payne@fda.hhs.gov

RUN apt-get update -y
RUN apt-get install gcc g++ make pkg-config -y

WORKDIR /tmp/
ADD https://github.com/agordon/libgtextutils/releases/download/0.7/libgtextutils-0.7.tar.gz /tmp/
RUN tar -xzf /tmp/libgtextutils-0.7.tar.gz
WORKDIR /tmp/libgtextutils-0.7
RUN ./configure
RUN make
RUN make install

WORKDIR /tmp/
ADD https://github.com/agordon/fastx_toolkit/releases/download/0.0.14/fastx_toolkit-0.0.14.tar.bz2 /tmp/
RUN tar -xjf /tmp/fastx_toolkit-0.0.14.tar.bz2
WORKDIR /tmp/fastx_toolkit-0.0.14
RUN ./configure
RUN make
RUN make install


RUN apt-get purge gcc make g++ pkg-config -y
RUN apt-get clean -y
