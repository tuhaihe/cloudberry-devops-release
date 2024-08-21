#!/bin/bash

set -euo pipefail

# Script Name: s3-repo-sync-and-sign.sh
#
# Description:
# This script automates AWS credentials configuration, secure GPG key handling,
# RPM repository synchronization from an S3 bucket, RPM signing, and repository metadata signing.
# It also exports and places the GPG public key in the repository for client use.
# Additionally, it supports a `s3-sync-only` mode to sync the S3 bucket to the local directory
# and exit after the operation completes.
#
# Usage:
# ./s3-repo-sync-and-sign.sh [-c] [-s <s3-bucket>] [-d <local-dir>] [-k <encrypted-key-file>] [-g <gpg-key-id>] [--upload-with-delete] [--s3-sync-only]
#
# Options:
#   -c                   : Configure AWS credentials using 'aws configure'.
#   -s <s3-bucket>       : Specify the S3 bucket and path to sync (required).
#   -d <local-dir>       : Specify the local directory to sync to (default: ~/repo).
#   -k <encrypted-key-file> : Specify the encrypted GPG private key file to import (optional).
#   -g <gpg-key-id>      : Specify the GPG key ID or email to use for signing (required for signing operations).
#   --upload-with-delete : Sync local changes to S3, deleting files in S3 that don't exist locally.
#   --s3-sync-only       : Perform only the S3 sync to the local directory, inform the user, and exit.
#   -h, --help           : Display this help and exit.

# Function to check if required commands are available
check_commands() {
  local cmds=("aws" "gpg" "shred" "createrepo" "rpm" "find")
  for cmd in "${cmds[@]}"; do
    if ! command -v "$cmd" &> /dev/null; then
      echo "Error: Required command '$cmd' not found. Please install it before running the script."
      exit 1
    fi
  done
}

# Function to display usage information
usage() {
  echo "Usage: $0 [-c] [-s <s3-bucket>] [-d <local-dir>] [-k <encrypted-key-file>] [-g <gpg-key-id>] [--upload-with-delete] [--s3-sync-only]"
  exit 1
}

# Parse options
GPG_KEY_ID=""
UPLOAD_WITH_DELETE=false
S3_SYNC_ONLY=false
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -c) CONFIGURE_AWS=true; shift ;;
    -s) S3_BUCKET="$2"; shift 2 ;;
    -d) LOCAL_DIR="$2"; shift 2 ;;
    -k) ENCRYPTED_KEY_FILE="$2"; shift 2 ;;
    -g) GPG_KEY_ID="$2"; shift 2 ;;
    --upload-with-delete) UPLOAD_WITH_DELETE=true; shift ;;
    --s3-sync-only) S3_SYNC_ONLY=true; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown option: $1"; usage ;;
  esac
done

# Check if required commands are available
check_commands

# Ensure S3 bucket is provided
if [ -z "${S3_BUCKET:-}" ]; then
  echo "Error: S3 bucket (-s) is required."
  usage
fi

# AWS credentials configuration (optional)
if [ "${CONFIGURE_AWS:-false}" = true ]; then
  echo "Configuring AWS credentials..."
  aws configure
fi

# Check access to the S3 bucket
echo "Checking access to S3 bucket $S3_BUCKET..."
if ! aws s3 ls "$S3_BUCKET" &> /dev/null; then
  echo "Error: Unable to access S3 bucket $S3_BUCKET. Please check your AWS credentials and permissions."
  exit 1
fi

# Sync the S3 repository to the local directory
mkdir -p "$LOCAL_DIR"
echo "Syncing S3 repository from $S3_BUCKET to $LOCAL_DIR..."
aws s3 sync "$S3_BUCKET" "$LOCAL_DIR"

# Check if the operation is `s3-sync-only`
if [ "$S3_SYNC_ONLY" = true ]; then
  echo "S3 sync operation completed successfully."
  exit 0
fi

# Decrypt and import GPG private key if not in sync-only mode
if [ -n "${ENCRYPTED_KEY_FILE:-}" ]; then
  DECRYPTED_KEY_FILE="${ENCRYPTED_KEY_FILE%.*}"
  echo "Decrypting GPG private key..."
  gpg --decrypt --output "$DECRYPTED_KEY_FILE" "$ENCRYPTED_KEY_FILE"

  # Check if the key is already imported
  if gpg --list-keys | grep -q "$GPG_KEY_ID"; then
    echo "GPG key already imported."
  else
    gpg --import "$DECRYPTED_KEY_FILE"
  fi

  # Securely delete the decrypted key file
  shred -u "$DECRYPTED_KEY_FILE"
fi

# Define the directories for `el8` and `el9` repositories
REPO_DIRS=("$LOCAL_DIR/el8/x86_64" "$LOCAL_DIR/el9/x86_64")

# Traverse each repository directory (el8 and el9) and sign RPMs
for REPO_DIR in "${REPO_DIRS[@]}"; do
  if [ -d "$REPO_DIR" ]; then
    echo "Processing repository at $REPO_DIR..."

    # Sign each RPM in the directory
    echo "Signing RPM packages in $REPO_DIR..."
    find "$REPO_DIR" -name "*.rpm" -exec rpm --addsign {} \;

    # Verify that RPMs were signed successfully
    echo "Verifying RPM signatures in $REPO_DIR..."
    find "$REPO_DIR" -name "*.rpm" -exec rpm -K {} \;

    # Recreate the repository metadata
    echo "Updating repository metadata in $REPO_DIR..."
    createrepo --update "$REPO_DIR"

    # Sign the repository metadata
    echo "Signing repository metadata in $REPO_DIR..."
    gpg --detach-sign --armor --local-user "$GPG_KEY_ID" "$REPO_DIR/repodata/repomd.xml"
  else
    echo "Warning: Repository directory $REPO_DIR does not exist. Skipping..."
  fi
done

# Export GPG public key for clients and place it in the root of the repository
echo "Exporting GPG public key..."
gpg --armor --export "$GPG_KEY_ID" > "$LOCAL_DIR/RPM-GPG-KEY-cloudberry"

# Optionally, place the public key in a specific directory (keys) within each repo
for REPO_DIR in "${REPO_DIRS[@]}"; do
  if [ -d "$REPO_DIR" ]; then
    mkdir -p "$REPO_DIR/keys"
    cp "$LOCAL_DIR/RPM-GPG-KEY-cloudberry" "$REPO_DIR/keys/RPM-GPG-KEY-cloudberry"
  fi
done

# Upload changes to S3 with --delete option if requested
if [ "$UPLOAD_WITH_DELETE" = true ]; then
  echo "Uploading local changes to S3 with --delete option..."
  aws s3 sync "$LOCAL_DIR" "$S3_BUCKET" --delete
  echo "S3 sync with --delete completed."
fi

# Print completion message
echo "S3 repository sync, RPM signing, metadata signing, and public key export completed successfully."
