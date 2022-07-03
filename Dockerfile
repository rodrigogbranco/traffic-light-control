FROM ubuntu:18.04

LABEL maintainer="Rodrigo Gonçalves de Branco (rodrigo.g.branco@gmail.com)"
LABEL Description="Dockerised Simulation of Urban MObility(SUMO) - SPreS-EV InterSCity"

ENV SUMO_VERSION 1.2.0
ENV SUMO_HOME /opt/sumo
ARG SUMO_USER

# Install system dependencies.
RUN apt-get update && apt-get -qq install \
    wget \
    g++ \
    make \
    libxerces-c-dev \
    libfox-1.6-0 libfox-1.6-dev \
    libgdal-dev libproj-dev \
    python cmake autoconf automake python-six python-requests python-numpy \
    python-zope.event \
    libtool \
    i965-va-driver \
    libgl1-mesa-dri

# Download and extract source code
RUN wget http://downloads.sourceforge.net/project/sumo/sumo/version%20$SUMO_VERSION/sumo-src-$SUMO_VERSION.tar.gz
RUN tar xzf sumo-src-$SUMO_VERSION.tar.gz && \
    mv sumo-$SUMO_VERSION $SUMO_HOME && \
    rm sumo-src-$SUMO_VERSION.tar.gz

# Configure and build from source.
RUN cd $SUMO_HOME && ./configure && make install

#RUN adduser $SUMO_USER --disabled-password
RUN useradd -ms /bin/bash $SUMO_USER

RUN mkdir -p /opt/spresev-sim

USER $SUMO_USER
WORKDIR /opt/spresev-sim

#ADD classes /opt/classes
#ADD runner.py /opt/runner.py
#ADD embedded.py /opt/embedded.py
#ADD scenarios /home/$SUMO_USER/scenarios/
#WORKDIR /home/$SUMO_USER/scenarios/

#VOLUME scenarios /scenarios

#RUN chmod -R 777 /home/$SUMO_USER/scenarios/

#RUN chown -R $SUMO_USER:$SUMO_USER /home/$SUMO_USER/scenarios/
# CMD sumo-gui