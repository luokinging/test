#!/bin/bash
#
# SAE Job Update and Execution Script
# Usage: ./sae-update-and-exec-job.sh <APP_ID> <TARGET_IMAGE> [JOB_NAME]
#
# Arguments:
#   APP_ID       - SAE Job Application ID
#   TARGET_IMAGE - Docker image URL to deploy
#   JOB_NAME     - Optional job name for logging (default: "Job")
#
# Environment:
#   Requires aliyun CLI to be installed and configured
#
# Exit codes:
#   0 - Success
#   1 - Failure (with error message)
#

set -e

# Arguments
APP_ID="${1:?Error: APP_ID is required}"
TARGET_IMAGE="${2:?Error: TARGET_IMAGE is required}"
JOB_NAME="${3:-Job}"

# Configuration
MAX_CHANGEORDER_ITERATIONS=30
CHANGEORDER_POLL_INTERVAL=2
MAX_JOBSTATUS_ITERATIONS=60
JOBSTATUS_POLL_INTERVAL=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${YELLOW}🔹 $*${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $*${NC}"
}

log_error() {
    echo -e "${RED}❌ $*${NC}"
}

# Step 1: Update Job Template
log_info "[1/4] Updating ${JOB_NAME} Template..."

UPDATE_RESP=$(aliyun sae UpdateJob --AppId "$APP_ID" --ImageUrl "$TARGET_IMAGE")
echo "$UPDATE_RESP"

CHANGE_ORDER_ID=$(echo "$UPDATE_RESP" | jq -r '.Data.ChangeOrderId // empty')

if [ -z "$CHANGE_ORDER_ID" ]; then
    log_error "Failed to get ChangeOrderId from UpdateJob response."
    exit 1
fi

echo "🔸 ChangeOrder ID: $CHANGE_ORDER_ID. Waiting for update to complete..."

# Step 2: Poll ChangeOrder status
log_info "[2/4] Polling ChangeOrder status..."

for k in $(seq 1 "$MAX_CHANGEORDER_ITERATIONS"); do
    CO_RESP=$(aliyun sae DescribeChangeOrder --ChangeOrderId "$CHANGE_ORDER_ID")
    CO_STATUS=$(echo "$CO_RESP" | jq -r '.Data.Status')

    # SAE ChangeOrder Status: 0=准备, 1=执行中, 2=执行成功, 3=执行失败, 6=终止
    if [ "$CO_STATUS" == "2" ]; then
        log_success "Update Job Template Succeeded!"
        break
    elif [ "$CO_STATUS" == "3" ] || [ "$CO_STATUS" == "6" ]; then
        log_error "Update Job Template Failed!"
        echo "$CO_RESP"
        exit 1
    else
        echo "⏳ Update in progress (Status: $CO_STATUS)... waiting ${CHANGEORDER_POLL_INTERVAL}s"
        sleep "$CHANGEORDER_POLL_INTERVAL"
    fi

    if [ "$k" -eq "$MAX_CHANGEORDER_ITERATIONS" ]; then
        log_error "Update Job Timed out"
        exit 1
    fi
done

# Step 3: Execute Job
log_info "[3/4] Triggering ${JOB_NAME} Execution..."

EXEC_OUTPUT=$(aliyun sae ExecJob --AppId "$APP_ID")
JOB_ID=$(echo "$EXEC_OUTPUT" | jq -r '.Data.Data // .Data.JobId // empty')

if [ -z "$JOB_ID" ] || [ "$JOB_ID" == "null" ]; then
    log_error "Failed to trigger job. API Output:"
    echo "$EXEC_OUTPUT"
    exit 1
fi

log_success "Job Triggered. Job ID: $JOB_ID"

# Step 4: Poll Job Status
log_info "[4/4] Polling ${JOB_NAME} Status..."

for i in $(seq 1 "$MAX_JOBSTATUS_ITERATIONS"); do
    STATUS_JSON=$(aliyun sae DescribeJobStatus --AppId "$APP_ID" --JobId "$JOB_ID")
    STATE=$(echo "$STATUS_JSON" | jq -r '.Data.State')

    # SAE Job State: 0=Pending, 1=Success, 2=Failed, 3=Running
    echo "Attempt $i: Job State Code: [$STATE]"

    if [ "$STATE" == "1" ]; then
        log_success "${JOB_NAME} Succeeded!"
        exit 0
    elif [ "$STATE" == "2" ]; then
        log_error "${JOB_NAME} Failed!"
        echo "Debug Info:"
        echo "$STATUS_JSON"
        exit 1
    elif [ "$STATE" == "3" ] || [ "$STATE" == "0" ]; then
        echo "⏳ Job is running/pending..."
    else
        echo "❓ Unknown State: $STATE"
    fi

    sleep "$JOBSTATUS_POLL_INTERVAL"
done

log_error "Job execution timed out."
exit 1
