FROM python:3.9-slim

# Install docker
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io && rm -rf /var/lib/apt/lists/*

# Install k6
ARG ARCH=amd64
ARG ARCH=arm64
ARG K6_VERSION=k6-v0.50.0-linux-$ARCH
ADD https://github.com/grafana/k6/releases/download/v0.50.0/$K6_VERSION.tar.gz $K6_VERSION.tar.gz
RUN tar -xzf $K6_VERSION.tar.gz
RUN mv $K6_VERSION/k6 /usr/bin/k6


# Setup calibrator
WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]
