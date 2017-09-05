FROM ubuntu:latest
MAINTAINER jj
EXPOSE 8080
RUN DBEIAN_FRONTEND=noninteractive apt-get update && \
   apt-get install python python-pip -y && \
   apt-get clean autoclean && \
   apt-get autoremove && \
   rm -rf /var/lib/{apt,dpkg,cache,log}
RUN mkdir /app/
ADD . /app/
RUN pip install -r /app/requirements.txt
WORKDIR /app/dashboard/
CMD python app.py
