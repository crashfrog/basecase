FROM crashfrog/basecase:latest
MAINTAINER Justin Payne, justin.payne@fda.hhs.gov

ADD https://s3.amazonaws.com/files.pacb.com/software/smrtanalysis/2.2.0/smrtanalysis-2.2.0.133377.run \tmp\
ADD https://s3.amazonaws.com/files.pacb.com/software/smrtanalysis/2.2.0/smrtanalysis-2.2.0.133377-patch-3.run \tmp\
EXPORT SMRT_ROOT=/opt/smrtanalysis
RUN mkdir $SMRT_ROOT
RUN chown smrtanalysis:smrtanalysis $SMRT_ROOT
WORKDIR /tmp/
USER smrtanalysis
RUN smrtanalysis-2.2.0.133377.run -p smrtanalysis-2.2.0.133377-patch-3.run --rootdir $SMRT_ROOT