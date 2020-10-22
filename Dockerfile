FROM ubuntu:latest
ENV PORT=80
WORKDIR /python/server
RUN apt-get update
RUN apt-get install -y python3
COPY Pypress .
COPY server.py .
CMD ["/bin/bash"]