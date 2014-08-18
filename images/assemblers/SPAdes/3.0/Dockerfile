FROM localhost:5000/basecase-basic
MAINTAINER Justin Payne, justin.payne@fda.hhs.gov

ADD http://spades.bioinf.spbau.ru/release3.0.0/SPAdes-3.0.0-Linux.tar.gz /tmp/
RUN tar xzf /tmp/SPAdes-3.0.0-Linux.tar.gz
WORKDIR /SPAdes-3.0.0-Linux
RUN mv bin/* /usr/local/bin/
RUN mv share/* /usr/local/share/