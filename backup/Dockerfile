FROM ubuntu:20.04

## Install docker
RUN apt-get update
RUN apt-get --no-install-recommends install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

RUN add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

RUN apt-get update
RUN apt-get --no-install-recommends install -y docker-ce docker-ce-cli containerd.io

# Install backup tool prerequesites
RUN apt-get --no-install-recommends install -y rsync mysql-client cron supervisor
RUN apt-get --no-install-recommends install -y python3 python3-pip python3-setuptools python3-wheel
RUN apt-get --no-install-recommends install -y nano

# Finished installation
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false
RUN rm -rf /var/lib/apt/lists/*


# Add backup script
RUN mkdir -p /scripts
COPY scripts/* /scripts/
RUN pip3 install -r /scripts/requirements.txt

# Copy backup cron file to the cron.d directory
COPY backup-cron /etc/cron.d/backup-cron
RUN chmod 0644 /etc/cron.d/backup-cron
RUN crontab /etc/cron.d/backup-cron
RUN touch /var/log/cron.log

RUN mkdir -p \
    /var/log/supervisord \
    /var/run/supervisord \
;

COPY supervisord.conf /

COPY env.sh /
RUN chmod 0700 /env.sh

# Run the supervisord command on container startup
CMD ["/usr/bin/supervisord", "-c", "/supervisord.conf"]
