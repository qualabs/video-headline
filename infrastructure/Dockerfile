FROM node:16

WORKDIR /usr/src/app

COPY . .

RUN yarn install

RUN yarn run build

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update  \
    && pip3 install boto3 \
    && apt-get install -y expect 

RUN curl "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install

RUN curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb" \
    && dpkg -i session-manager-plugin.deb \
    && rm -rf /var/lib/apt/lists/*

ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_SESSION_TOKEN=""

# CMD ["yarn", "cdk", "bootstrap", "--profile", "$AWS_PROFILE"] && \
#     ["yarn", "cdk", "deploy", "'*'", "--profile", "$AWS_PROFILE"]

CMD /bin/bash -c 'export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID && export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY && export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN && \
    read -p "Enter username: " username && \
    read -p "Enter email: " email && \
    read -p "Enter password: " password && \
    python3 create_super_user.py $username $email $password'