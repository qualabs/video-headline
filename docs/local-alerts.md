
# Use alerts in local enviroment

Since AWS SNS needs an endpoint to send notifications (In this case an URL), it's needed to create a public url to expose our local machine for sns usage.

## Recommendation:
  - Ngrok


Ounce we have the url, change the BASE_URL env variable for video-hub service in the env file:
  - BASE_URL=https://EXAMPLE_URL/