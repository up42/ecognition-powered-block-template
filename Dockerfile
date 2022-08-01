FROM ecognition/linux_cle:10.2.1 AS ecognition_cle

FROM centos/python-38-centos7
COPY --from=ecognition_cle ["/opt/eCognition Cmd Engine", "/opt/eCognition Cmd Engine"]

ENV ECOG_CONFIG_logging="log path=/tmp/logs;trace level=Detailed"
ENV LM_LICENSE_FILE="@ecognition-license-server.ecognition.svc"

# The manifest file contains metadata for correctly building and
# tagging the Docker image. This is a build time argument.
ARG BUILD_DIR=.
ARG manifest
LABEL "up42_manifest"=$manifest

COPY $BUILD_DIR /block
RUN pip3 install -r /block/requirements.txt

WORKDIR /opt/"eCognition Cmd Engine"/bin

CMD ["python3", "/block/src"]