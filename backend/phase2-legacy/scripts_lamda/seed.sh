#!/usr/bin/env bash
set -euo pipefail
: "${AWS_REGION:=ap-southeast-1}"
PARAM="/aap/app/DATABASE_URL"
DBURL="$(aws ssm get-parameter --name "$PARAM" --with-decryption --region "$AWS_REGION" --query Parameter.Value --output text)"
psql "$DBURL" -f seed/seed.sql
