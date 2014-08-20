FROM localhost:5000/basecase-basic-jre
MAINTAINER Justin Payne, justin.payne@fda.hhs.gov

RUN apt-get install build-essential lsb-release -y

ADD https://s3.amazonaws.com/files.pacb.com/software/smrtanalysis/2.2.0/smrtanalysis-2.2.0.133377.run /tmp/
ADD https://s3.amazonaws.com/files.pacb.com/software/smrtanalysis/2.2.0/smrtanalysis-2.2.0.133377-patch-3.run /tmp/

EXPOSE 80

ENV SMRT_ROOT /opt/smrtanalysis
RUN mkdir $SMRT_ROOT
RUN useradd smrtanalysis
RUN echo "smrtanalysis" | passwd smrtanalysis --stdin
RUN chown smrtanalysis:smrtanalysis $SMRT_ROOT
WORKDIR /tmp/
USER smrtanalysis
RUN smrtanalysis-2.2.0.133377.run -p smrtanalysis-2.2.0.133377-patch-3.run --rootdir $SMRT_ROOT

RUN $SMRT_ROOT/admin/bin/smrtportald-initd start
RUN $SMRT_ROOT/admin/bin/kodosd start

RUN apt-get clean
RUN apt-get autoclean