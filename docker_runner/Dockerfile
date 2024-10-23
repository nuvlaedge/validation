FROM docker AS docker
FROM ubuntu:24.10

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt upgrade -y && useradd -m runner

COPY --from=docker /usr/local/bin/docker /usr/bin/docker

RUN apt install -y curl \
            wget \
            lsb-release \
            libicu-dev \
            libssl-dev \
            libkrb5-dev \
            sudo \
            zlib1g


RUN mkdir /home/runner/actions-runner

WORKDIR /home/runner/actions-runner

RUN curl -o actions-runner-linux-x64-2.320.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.320.0/actions-runner-linux-x64-2.320.0.tar.gz

RUN tar xzf ./actions-runner-linux-x64-2.320.0.tar.gz
#
RUN ./bin/installdependencies.sh
#
COPY start_runner.sh start_runner.sh

# Add runner to docker group
RUN groupadd docker && usermod -aG docker runner
RUN echo "runner ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/runner

# Make runner configure and execute the GH runner
RUN chown -R runner ~runner

USER root

RUN chmod +x start_runner.sh


ENTRYPOINT ["bash", "start_runner.sh"]
