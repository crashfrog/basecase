FROM localhost:5000/basecase-basic-jre
MAINTAINER Justin Payne, justin.payne@fda.hhs.gov

RUN apt-get install build-essential lsb-release -y

WORKDIR /tmp/
RUN curl -O https://s3.amazonaws.com/files.pacb.com/software/smrtanalysis/2.2.0/smrtanalysis-2.2.0.133377.run
RUN curl -O https://s3.amazonaws.com/files.pacb.com/software/smrtanalysis/2.2.0/smrtanalysis-2.2.0.133377-patch-3.run

RUN apt-get install rsync -y

EXPOSE 80

ENV SMRT_ROOT /opt/smrtanalysis
RUN mkdir -p /opt/smrtanalysis/
RUN useradd smrtanalysis -p 'mkpasswd smrtanalysis'
#RUN echo "smrtanalysis" | passwd smrtanalysis --stdin
RUN chown smrtanalysis:smrtanalysis $SMRT_ROOT
RUN chown smrtanalysis:smrtanalysis /tmp/*
WORKDIR /tmp/
USER smrtanalysis
RUN chmod 755 /tmp/*
RUN ./smrtanalysis-2.2.0.133377.run -p smrtanalysis-2.2.0.133377-patch-3.run --rootdir $SMRT_ROOT

RUN $SMRT_ROOT/admin/bin/smrtportald-initd start
RUN $SMRT_ROOT/admin/bin/kodosd start

RUN apt-get clean
RUN apt-get autoclean