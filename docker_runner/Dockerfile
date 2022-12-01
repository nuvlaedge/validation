FROM ubuntu:22.04

ARG RUNNER_VERSION
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -y && apt upgrade -y && useradd -m runner

RUN apt install -y curl

RUN mkdir /home/runner/actions-runner

WORKDIR /home/runner/actions-runner

RUN curl -o actions-runner-linux-x64-2.299.1.tar.gz -L  \
    https://github.com/actions/runner/releases/download/v2.299.1/actions-runner-linux-x64-2.299.1.tar.gz

RUN tar xzf ./actions-runner-linux-x64-2.299.1.tar.gz

RUN ./bin/installdependencies.sh

COPY start_runner.sh start_runner.sh

# Make runner configure and execute the GH runner
RUN chown -R runner ~runner

USER runner

RUN chmod +x start_runner.sh


ENTRYPOINT ["bash", "start_runner.sh"]
