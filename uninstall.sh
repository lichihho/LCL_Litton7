#!/bin/bash
#
# Ininstall script for Litton7-Public, require root previledge
#
# This script will not remove user 'lclwebservice' due to lclwebservice is
# the user of all lab's web service.
set -e

PROJECT="litton7-public"
IMAGE_NAME='lclab/litton7-public'
IMAGE_VERSION='0.0.0'

systemctl stop "$IMAGE_NAME"

docker image rm "$IMAGE_NAME:$IMAGE_VERSION"
docker image rm "$IMAGE_NAME:latest"

rm "/etc/systemd/system/$PROJECT.service"
rm -rf "/opt/$PROJECT"

systemctl daemon-reload
