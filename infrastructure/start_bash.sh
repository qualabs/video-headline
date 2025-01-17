#!/bin/sh

# Get AWS region from environment variable or default to us-east-1
aws_region="${AWS_DEFAULT_REGION:-us-east-1}"

# Get cluster and task information
cluster="Videoheadline-cluster"
task_arn=$(aws ecs list-tasks --cluster $cluster --launch-type "FARGATE" --query "taskArns[0]" --output text --region $aws_region)

# Execute create_super_user.sh inside the container
aws ecs execute-command \
    --cluster $cluster \
    --task $task_arn \
    --container video-hub \
    --interactive \
    --command "bash" \
    --region $aws_region