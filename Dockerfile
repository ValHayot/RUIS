from ubuntu

ENV COLLECTL_VERSION 4.8.3
ENV DEBIAN_FRONTEND noninteractive

RUN : \
    && apt-get update -y \
    && apt-get upgrade -y \
    && apt-get -qq install \
    wget \
    collectl \
    && wget http://master.dl.sourceforge.net/project/collectl-utils/collectl-utils-${COLLECTL_VERSION}/collectl-utils-${COLLECTL_VERSION}.src.tar.gz \
    && tar xf collectl-utils-${COLLECTL_VERSION}.src.tar.gz \
    && cd collectl-utils-${COLLECTL_VERSION} \
    && ./INSTALL \
    && apt-get remove -y wget \
    && rm -rf /var/lib/apt/lists/* \
    && :
RUN : \
    && apt-get update -y \
    && apt-get upgrade -y \
    && apt-get -qq install \
    man-db \
    && :

COPY . /ruis

ENTRYPOINT [ "collectl" ]
