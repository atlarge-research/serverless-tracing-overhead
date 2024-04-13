FROM eclipse-temurin:17 as jre-build

# Create a custom Java runtime
RUN $JAVA_HOME/bin/jlink \
         --add-modules ALL-MODULE-PATH \
         --strip-debug \
         --no-man-pages \
         --no-header-files \
         --compress=2 \
         --output /javaruntime

FROM maven:3.8.5-openjdk-17-slim as maven
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH "${JAVA_HOME}/bin:${PATH}"
COPY --from=jre-build /javaruntime $JAVA_HOME

RUN mvn -version
WORKDIR /spring
COPY src src
COPY pom.xml pom.xml
RUN mvn package -q

FROM debian:bullseye-slim
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH "${JAVA_HOME}/bin:${PATH}"

COPY --from=jre-build /javaruntime $JAVA_HOME

RUN java -version
WORKDIR /spring
COPY --from=maven /spring/target/hello-spring-1.0-SNAPSHOT.jar app.jar

EXPOSE 8080

ARG OPENTELEMETRY=false
ARG OPENTELEMETRY_VERSION=v2.3.0

# Download OpenTelemetry Java agent
RUN if [ "$OPENTELEMETRY" = "true" ]; then \
    apt-get update && apt-get install -y wget && \
    wget -O /spring/opentelemetry-javaagent.jar https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/$OPENTELEMETRY_VERSION/opentelemetry-javaagent.jar \
    ; fi

ARG ELASTIC_APM=false
COPY --from=docker.elastic.co/observability/apm-agent-java:latest /usr/agent/elastic-apm-agent.jar /spring/elastic-apm-agent.jar

CMD ["java", "-server", "-XX:+UseNUMA", "-XX:+UseG1GC", "-XX:+DisableExplicitGC", "-XX:+UseStringDeduplication", "-Dlogging.level.root=INFO", "-jar", "app.jar", "--spring.profiles.active=jpa"]
