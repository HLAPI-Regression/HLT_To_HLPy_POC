# Use the Ubuntu 24.04 base image
FROM ubuntu:24.04
ARG DEBIAN_FRONTEND=noninteractive
ARG PYATS_VERSION=26.3
ARG IXNET_URL=https://downloads.ixiacom.com/support/downloads_and_updates/public/IxNetwork/26.0.0/26.0.2601.6/IxNetworkAPI26.0.2601.6Linux64.bin.tgz
ENV TZ=US/Pacific
 
# Update and install necessary packages
RUN apt -y update \
&& apt -y upgrade \
&& apt -y install build-essential wget python3 python3-setuptools python3-tk tclx8.4 python3-pip python3.12-venv openjdk-8-jdk \
&& rm -rf /var/lib/apt/lists/*
 
# Set the working directory
WORKDIR /opt
 
# Copy everything from the local directory into the container
COPY ./*.py .
COPY ./server .
COPY ./server/server.py .
 
# Download and install IxNetwork API silently
RUN IXNET_FILE=$(basename "${IXNET_URL}") \
    && IXNET_BIN="${IXNET_FILE%.tgz}" \
    && wget --no-check-certificate "${IXNET_URL}" \
    && tar -xvzf "${IXNET_FILE}" \
    && chmod +x "${IXNET_BIN}" \
    && ./"${IXNET_BIN}" -i silent \
    && rm -rf ./"${IXNET_FILE}" ./"${IXNET_BIN}"
 
# Install Python packages required by IxNetwork API
RUN rm -rf /usr/lib/python3.12/EXTERNALLY-MANAGED

# Create venv
RUN python3 -m venv /opt/venv

# Make venv the default Python/pip in the image
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Discover installed versions, install pip deps, and write startup script
RUN THE_IXNET=$(ls /opt/ixia/ixnetwork/) \
    && THE_HLAPI=$(ls /opt/ixia/hlapi/) \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install -r "/opt/ixia/ixnetwork/${THE_IXNET}/lib/PythonApi/requirements.txt" \
    && python3 -m pip install flask gunicorn \
    && python3 -m pip install "pyats==${PYATS_VERSION}" \
    && python3 -m pip install "pyats.tcl==${PYATS_VERSION}" \
    && { \
        echo '#!/bin/bash'; \
        echo "export THE_HLAPI=${THE_HLAPI}"; \
        echo "export THE_IXNET=${THE_IXNET}"; \
        echo "export HLPY=/opt/ixia/hlapi/${THE_HLAPI}/library/common/ixiangpf/python"; \
        echo "export IXNETPY=/opt/ixia/ixnetwork/${THE_IXNET}/lib/PythonApi/"; \
        echo "export IXNETLIBPATH=/opt/ixia/ixnetwork/${THE_IXNET}/lib/TclApi/"; \
        echo "export HLTTLIBPATH=/opt/ixia/hlapi/${THE_HLAPI}/"; \
        echo "export WEBSOCK=/opt/venv/lib/python3.12/site-packages"; \
        echo 'export TCLLIBPATH="${IXNETLIBPATH} ${HLTTLIBPATH}"'; \
        echo 'export PYTHONPATH="${HLPY}:${IXNETPY}:${WEBSOCK}"'; \
        #echo 'exec python3 /opt/server.py'; \
    } > /opt/setup_ixia_env.sh \
    && chmod +x /opt/setup_ixia_env.sh

# Start Flask server
EXPOSE 8000
CMD ["python3", "/opt/server.py"]
