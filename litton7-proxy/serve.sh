#!/bin/bash
# container entrypoint for LaDeco-Public-Proxy
#
# This script:
# 1. Checks for the existence of the certificate directory and `cert.conf` file.
# 2. Retrieves the SSL certificate and key file paths from the `cert.conf` file.
# 3. Sets the environment variables `SSL_KEYFILE` and `SSL_CERTFILE` for Uvicorn.
# 4. Starts the Uvicorn server on `0.0.0.0:8000` with SSL support.
#
# Error Codes:
# 1 - Missing certificate directory.
# 2 - Missing `cert.conf` file.
# 3 - Missing SSL certificate file in `cert.conf`.
# 4 - Missing SSL key file in `cert.conf`.
#
# Usage:
# 1. Ensure that the certificate directory and `cert.conf` are correctly set up.
# 2. Execute the script using `./start.sh`.

host_cert_dir='/etc/www/certs/'
cert_conf="${host_cert_dir%%/}/cert.conf"

# Function to check the existence of the certificate directory and cert.conf file.
# This function checks if the certificate directory and `cert.conf` exist.
# If either is missing, it returns an appropriate error code.
check_cert_directory_and_conf() {
  if [ ! -d "$host_cert_dir" ]; then
    return 1
  fi

  if [ ! -f "$cert_conf" ]; then
    return 2
  fi
}

# Function to retrieve SSL certificate file.
# This function retrieves the SSL certificate file path from the `cert.conf` file ($1).
# It returns an error code 1 if the certificate file is not found.
#
# param: $1 - path to cert.conf in Synoloty's system
synology_ssl_certificate() {
  local certfile certpath cert_conf

  cert_conf="$1"
  certfile=$(grep -m 1 'ssl_certificate ' "$cert_conf" | awk '{print $2}' | xargs basename | sed 's/;//')

  if [ -z "$certfile" ]; then
    return 1
  fi

  echo "${host_cert_dir%%/}/$certfile"
}

# Function to retrieve SSL key file.
# This function retrieves the SSL key file path from the `cert.conf` file ($1).
# It returns an error code 1 if the key file is not found.
#
# param: $1 - path to cert.conf in Synoloty's system
synology_ssl_key() {
  local keyfile keypath cert_conf

  cert_conf="$1"
  keyfile=$(grep -m 1 'ssl_certificate_key ' "$cert_conf" | awk '{print $2}' | xargs basename | sed 's/;//')

  if [ -z "$keyfile" ]; then
    return 1
  fi

  echo "${host_cert_dir%%/}/$keyfile"
}

## Main #############################################

if ! check_cert_directory_and_conf; then
  error_code="$?"
  case "$error_code" in
  1) echo "Error: Certification directory '$host_cert_dir' does not exist." >&2 ;;
  2) echo "Error: cert.conf file '$cert_conf' does not exist." >&2 ;;
  esac
  exit "$error_code"
fi

certpath="$(synology_ssl_certificate "$cert_conf")"
if [ -z "$certpath" ]; then
  echo "Error: SSL certificate file not found in '$cert_conf'." >&2
  exit 3
fi

keypath="$(synology_ssl_key "$cert_conf")"
if [ -z "$keypath" ]; then
  echo "Error: SSL key file not found in '$cert_conf'." >&2
  exit 4
fi

uvicorn server:app \
  --ssl-keyfile="$keypath" \
  --ssl-certfile="$certpath" \
  --host=0.0.0.0 \
  --port=8000
