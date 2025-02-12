ARG ALPINE_MAJ_MIN_VERSION="3.20"
ARG PYTHON_MAJ_MIN_VERSION="3.12"
ARG VALIDATION_AUTHORIZED_KEY
ARG VALIDATION_ADMIN_KEY

ARG BASE_IMAGE=ubuntu:24.04

FROM docker AS docker
FROM ${BASE_IMAGE} AS ssh-image

ARG VALIDATION_AUTHORIZED_KEY
ARG VALIDATION_ADMIN_KEY

COPY --from=docker /usr/local/bin/docker /usr/bin/docker
COPY --from=docker /usr/local/libexec/docker/cli-plugins/docker-compose /usr/local/libexec/docker/cli-plugins/docker-compose

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y openssh-client openssh-server openssl tini

RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
COPY authorized_keys /root/.ssh/authorized_keys

RUN mkdir -p /run/sshd
COPY --chown=root:root --chmod=755 entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/usr/bin/tini", "--", "/entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D", "-e"]
