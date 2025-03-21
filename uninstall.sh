#!/bin/bash
#
# Ininstall script for Litton7-Internal, require root previledge
#
# This script will not remove user 'lclwebservice' due to lclwebservice is
# the user of all lab's web service.
set -e

PROJECT="litton7-internal"
IMAGE_NAME='lclab/litton7-internal'
IMAGE_VERSION='0.0.0'

systemctl stop "$PROJECT"

docker image rm "$IMAGE_NAME:$IMAGE_VERSION"
docker image rm "$IMAGE_NAME:latest"

rm "/etc/systemd/system/$PROJECT.service"
rm -rf "/opt/$PROJECT"

systemctl daemon-reload
