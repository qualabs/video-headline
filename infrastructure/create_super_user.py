import boto3
import os

def main():
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")

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