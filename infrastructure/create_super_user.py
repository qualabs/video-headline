import boto3
import os
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

def show_message(username, email, password):
    url_aws = os.environ.get("VIDEO_HEADLINE_CDN_URL")
    message = (
        f"{Fore.GREEN}{Style.BRIGHT}Deploy successful!{Style.RESET_ALL}\n"
        f"\n" 
        f"Your Videohealine instance is deployed on: {Fore.BLUE}{url_aws}{Style.RESET_ALL}\n"
        f"Your admin access is on: {Fore.BLUE}{url_aws}/admin{Style.RESET_ALL}\n"
        f"\n" 
        f"Superuser created with the following credentials:\n"
        f"User: {Fore.CYAN}{username}{Style.RESET_ALL}\n"
        f"Password: {Fore.CYAN}{password}{Style.RESET_ALL}\n"
        f"Email: {Fore.CYAN}{email}{Style.RESET_ALL}"
    )
    ancho_recuadro = len(max(message.split('\n'), key=len)) + 4
    recuadro = f"{Fore.WHITE}{Back.BLACK}{'*' * ancho_recuadro}{Style.RESET_ALL}"
    
    print(recuadro)
    print(f"{Fore.WHITE}{Back.BLACK}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{Back.BLACK}{message}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{Back.BLACK}{Style.RESET_ALL}")
    print(recuadro)

def main():
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    region_name = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    if not region_name:
        region_name = "us-east-1"
    client = boto3.client("ecs", region_name=region_name)

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
        --command "./create_super_user.sh {username} {email} {password}" --region {region_name}'
    )
    show_message(username, email, password)


if __name__ == "__main__":
    main()