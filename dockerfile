# Use the Ubuntu 24.04 base image
FROM ubuntu:24.04
ARG DEBIAN_FRONTEND=noninteractive
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
 
# Download and install IxNetwork API silently
RUN wget https://downloads.ixiacom.com/support/downloads_and_updates/public/IxNetwork/26.0.0/26.0.2601.6/IxNetworkAPI26.0.2601.6Linux64.bin.tgz
RUN tar -xvzf IxNetworkAPI26.0.2601.6Linux64.bin.tgz
RUN chmod +x IxNetworkAPI26.0.2601.6Linux64.bin
RUN ./IxNetworkAPI26.0.2601.6Linux64.bin -i silent
RUN rm -rf ./IxNetworkAPI26.0.2601.6Linux64.bin*
 
# Install Python packages required by IxNetwork API
RUN rm -rf /usr/lib/python3.12/EXTERNALLY-MANAGED

# Create venv
RUN python3 -m venv /opt/venv

# Make venv the default Python/pip in the image
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install required pip dependencies
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r /opt/ixia/ixnetwork/26.0.2601.6/lib/PythonApi/requirements.txt
RUN python3 -m pip install flask gunicorn

# Set API library paths

ENV THE_HLAPI=26.0.2601.5 \
    THE_IXNET=26.0.2601.6

ENV HLPY="/opt/ixia/hlapi/${THE_HLAPI}/library/common/ixiangpf/python" \
    IXNETPY="/opt/ixia/ixnetwork/${THE_IXNET}/lib/PythonApi/" \
    IXNETLIBPATH="/opt/ixia/ixnetwork/${THE_IXNET}/lib/TclApi/" \
    HLTTLIBPATH="/opt/ixia/hlapi/${THE_HLAPI}/" \
    WEBSOCK="/opt/venv/lib/python3.12/site-packages"

ENV TCLLIBPATH="${IXNETLIBPATH} ${HLTTLIBPATH}"
ENV PYTHONPATH="${HLPY}:${IXNETPY}:${WEBSOCK}"

# Start Flask server
EXPOSE 8000
CMD ["python3", "server.py"]
