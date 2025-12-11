FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install utilities and .NET runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl jq bash-completion procps iputils-ping netcat-traditional \
    libicu74 libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Install .NET 8 SDK
RUN curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --channel 8.0 --install-dir /usr/share/dotnet \
    && ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet

# Install uv system-wide (modern Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx

# Install just (command runner)
RUN curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# base image already has user 'vscode' with good perms
USER vscode
WORKDIR /workspace
