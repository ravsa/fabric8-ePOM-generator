FROM centos:7
MAINTAINER Ravindra Ratnawat <ravindra@redhat.com>

VOLUME ["/target"]
CMD ["/usr/bin/bash"]

ENV LANG=en_US.utf8
ENV USER_NAME pyuser

RUN yum install -y epel-release && yum -y -q install git java java-devel which python34-pip python34-devel &&\
    yum clean all

#FIXME by using scl https://bugzilla.redhat.com/show_bug.cgi?id=1402447
RUN curl -O http://www.eu.apache.org/dist/maven/maven-3/3.5.3/binaries/apache-maven-3.5.3-bin.tar.gz &&\
    tar xzf apache-maven-3.5.3-bin.tar.gz &&\
    rm -f apache-maven-3.5.3-bin.tar.gz &&\
    mkdir /usr/local/maven &&\
    mv apache-maven-3.5.3/ /usr/local/maven/ &&\
    alternatives --install /usr/bin/mvn mvn /usr/local/maven/apache-maven-3.5.3/bin/mvn 1 &&\
    alternatives --set mvn /usr/local/maven/apache-maven-3.5.3/bin/mvn

ENV JAVA_HOME /usr/lib/jvm/java-openjdk

RUN useradd --user-group --create-home --shell /bin/false ${USER_NAME}

ENV HOME /home/${USER_NAME}

WORKDIR ${HOME}

COPY . ./


RUN chown -R ${USER_NAME}:${USER_NAME} ./*
RUN pip3 install -r requirements.txt

USER ${USER_NAME}
