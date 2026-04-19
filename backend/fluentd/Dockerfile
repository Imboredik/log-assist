FROM fluent/fluentd:v1.17-debian-1

USER root
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev curl netcat-openbsd && \
    fluent-gem install fluent-plugin-postgres && \
    fluent-gem install fluent-plugin-elasticsearch && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER fluent
ENTRYPOINT ["tini",  "--", "/bin/entrypoint.sh"]
CMD ["fluentd"]