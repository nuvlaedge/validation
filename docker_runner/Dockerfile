FROM docker AS docker
FROM alpine:3.20

ENV DEBIAN_FRONTEND=noninteractive

RUN apk update && adduser -S runner

COPY --from=docker /usr/local/bin/docker /usr/bin/docker

RUN apk add curl \
            wget \
            lsb-release \
            bash


RUN mkdir /home/runner/actions-runner

WORKDIR /home/runner/actions-runner

RUN curl -o actions-runner-linux-x64-2.320.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.320.0/actions-runner-linux-x64-2.320.0.tar.gz

RUN tar xzf ./actions-runner-linux-x64-2.320.0.tar.gz
#
#RUN ./bin/installdependencies.sh
#
COPY start_runner.sh start_runner.sh

# Make runner configure and execute the GH runner
RUN chown -R runner ~runner

USER runner

RUN chmod +x start_runner.sh


ENTRYPOINT ["bash", "start_runner.sh"]
