# Video Headline - Contributing

## Table of Contents

- [Running the application in local environment](#running-the-application-in-local-environment)
- [How to build the player](#how-to-build-the-player)
- [How to build the docker](#how-to-build-the-docker)
- [How to run the tests](#how-to-run-the-tests)
- [How to use the linters](#how-to-use-the-linters)

### Running the application in local environment

To set up the project locally, follow the instructions provided below.

#### Prerequisites

- AWS Account: Necessary for hosting and delivering video content.
- Docker and Docker compose: Video Headline runs inside Docker containers, so it is necessary to have Docker and Docker Compose installed.
- Yarn and Node.js(v10): Required to deploy AWS configurations and build the playerReact component.
- Python: Necessary for running Django and other Python-based tools.
- AWS CLI: Useful for configuring and managing AWS services from the command line.

#### Create .env file

Create a .env file at the root of the project with all the variables defined in the .env-example file and their respective values.

#### Set up and running the application

Follow these steps to set up and run the application locally:

1. Create a symbolic link to the appropriate Docker Compose file (`docker-compose.dev.yml` or `docker-compose.prod.yml`) for your environment using `ln -s docker-compose.dev.yml docker-compose.yml`.
2. Run `docker-compose up`.
3. Run `docker exec -it video-hub bash` to access the video-hub container.
4. Create a superuser for admin access running `python manage.py createsuperuser`.
5. Go to `http://localhost:8010/admin` and log in with the superuser credentials.

### How to build the player

In Videoheadline we use the playerReact component to play the videos. This component is built using React and it is compiled to a CSS and JS file that are used in the Django template that renders the player.
If you need to make changes to the player, you need to follow the steps below to build the player and test it in Videoheadline.

#### Steps to create a new version of the Videoheadline playerReact:

1. Make the changes and compile using npm run build.
2. Copy the compiled CSS and JS to player/static/player/css and player/static/player/js, respectively.
3. Delete the old CSS and JS files in player/static/player/css and player/static/player/js.
4. In the player/templates/player/index.html template, change the names of the CSS and JS files to which the template points.
5. Test in Videoheadline to ensure that the player is working correctly.

#### Important Notes:

When modifying the player, ensure that it continues working in IE 11 on Windows 10 and 8.1. It doesn´t work on Windows 7 with IE 11.

### How to build the docker

### How to run the tests

### How to use the linters

If you want to contribute to the project, it is important to use the linters to ensure that the code is consistent and follows the best practices. The linters used in the project are ESLint for JavaScript and Flake8 for Python. In addition, we use Prettier to format the JavaScript code and Black to format the Python code.

#### Setting Up ESLint for Linting React in Visual Studio Code

Follow the steps below to set up ESLint for linting React code in Visual Studio Code:

1. Prerequisites:

- Navigate to the `web` folder of the project.

2. Installation:

- Run the command `npm install` to install necessary packages.

3. Configuring Visual Studio Code:

- Ensure you have the following extensions installed:

<img src="docs/eslint_extension.png" alt="drawing" width="400"/>
<img src="docs/prettier_eslint_extension.png" alt="drawing" width="400"/>

- Accessing settings:
  - To open the command palette in Visual Studio Code, press Ctrl + Shift + P and select:

<img src="docs/vsc_settings.png" alt="drawing" width="400"/>

- Append the following configurations:
  ```json
  "editor.codeActionsOnSave": { "source.fixAll.eslint": true },
  "editor.formatOnSave": true,
  "[javascriptreact]": {
  	"editor.defaultFormatter": "rvest.vs-code-prettier-eslint"
    },
    "[json]": {
  	"editor.defaultFormatter": "rvest.vs-code-prettier-eslint"
  }
  ```

With these configurations, your React code will be automatically linted and formatted.

#### Setting Up Flake8 and Black for Linting and Formatting Python in Visual Studio Code
