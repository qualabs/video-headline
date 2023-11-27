import boto3
import os
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python create_super_user.py <username> <email> <password>")
        sys.exit(1)

    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]

    client = boto3.client("ecs", region_name="us-east-1")

    cluster = "Videoheadline-cluster"
    # Get cluster tasks
    response = client.list_tasks(
        cluster=cluster,
        launchType="FARGATE",
    )

    # Describe cluster tasks
    response = client.describe_tasks(
        cluster=cluster,
        tasks=response["taskArns"],
    )

    # Get the task containing the video-hub container
    filter_task = filter(
        lambda task: any(
            "video-hub" == container["name"] for container in task["containers"]
        ),
        response["tasks"],
    )
    [video_hub_task] = list(filter_task)
    task_arn = video_hub_task["taskArn"]

    # Execute create_super_user.sh inside the container
    os.system(
        f'unbuffer aws ecs execute-command --cluster {cluster} \
        --task {task_arn} \
        --container video-hub --interactive \
        --command "./create_super_user.sh {username} {email} {password}"  --region us-east-1'
    )


if __name__ == "__main__":
    main()