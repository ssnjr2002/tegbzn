FROM phusion/baseimage:bionic-1.0.0

# Use baseimage-docker's init system:
CMD ["/sbin/my_init"]

# Install dependencies:
RUN apt-get update \
 && apt-get install -y \
    bash curl sudo wget \
    python3 unzip sed \
    python3-pip unzip \
 && pip3 install requests

# Clean up APT:
RUN apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set work dir:
WORKDIR /home

# Install NZBGET and rclone:
RUN wget https://nzbget.net/download/nzbget-latest-bin-linux.run \
 && bash nzbget-latest-bin-linux.run \
 && curl https://rclone.org/install.sh | sudo bash

# Create required dirs:
RUN mkdir -p /home/nzbget/maindir/ \
 && mkdir -p /home/.config/rclone/

# Copy files:
COPY start /home/
COPY rclone_pp.py /home/nzbget/scripts/
COPY ping.py /home/

# Run NZBGET:
CMD bash /home/start
