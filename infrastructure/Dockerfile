FROM node:16

WORKDIR /usr/src/app

COPY . .

RUN yarn install

RUN yarn run build

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN curl "https://d1vvhvl2y92vvt.cloudfront.net/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install

ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_SESSION_TOKEN=""

# CMD ["yarn", "cdk", "bootstrap", "--profile", "$AWS_PROFILE"] && \
#     ["yarn", "cdk", "deploy", "'*'", "--profile", "$AWS_PROFILE"]

CMD /bin/bash -c 'export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID && export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY && export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN && yarn cdk bootstrap && yarn cdk deploy "*"'
