#!/bin/bash
#
# Installation script for LaDeco-Internal, require root previlege.
#
set -e

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root"
  exit 1
fi

PROJECT=litton7-internal
APP_USER="lclwebservice"
APP_DIR="/opt/$PROJECT"
SERVICE_FILE="$PROJECT.service"
SERVICE_PATH="$APP_DIR/$SERVICE_FILE"
SYSTEMD_SERVICE_PATH="/etc/systemd/system/$SERVICE_FILE"
IMAGE_NAME='lclab/litton7-internal'
IMAGE_VERSION='0.0.0'

waiting_for() {
  local duration=$1 # in seconds
  local spinner="|/-\\"
  local i=0
  local end_time=$((SECONDS + duration))

  set +e
  while [ $SECONDS -lt $end_time ]; do
    printf "\r%s" "${spinner:i%4:1}"
    ((i++))
    sleep 0.1
  done
  set -e

  printf '\n'
}

if ! id "$APP_USER" &>/dev/null; then
  useradd --no-create-home --system --shell /bin/false "$APP_USER"
fi

# Check if target directory exists and handle it
if [ -d "$APP_DIR" ]; then
  echo "Directory $APP_DIR already exists. Creating backup..."
  mv "$APP_DIR" "$APP_DIR.$(date +%Y%m%d%H%M%S).bak"
fi

mkdir -p "$APP_DIR"
cp -r . "$APP_DIR"
mkdir -p "$APP_DIR/logs"
ln -sf "$SERVICE_PATH" "$SYSTEMD_SERVICE_PATH"
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

docker build -t "$IMAGE_NAME:$IMAGE_VERSION" -t "$IMAGE_NAME:latest" .

docker compose up -d >/dev/null
printf 'initialize service...  '; waiting_for 10
docker compose down

systemctl daemon-reload && systemctl start "$PROJECT" && {
  printf 'start service...  '; waiting_for 30

  echo 'service installed successfully'
  echo "use 'systemctl status $PROJECT' to check status of the service"
  echo "log will be recorded to service journal. Please use 'journalctl -u $PROJECT' to browse logs"
  echo

  [ -f ./.env ] && source ./.env
  echo "now you can open browser and navigate to http://${HOST_IP:-localhost}:${HOST_PORT}"
}
