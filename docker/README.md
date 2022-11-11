Weladee for developer

## requirement

1. docker +20.10 with docker-compose-plugin [see](https://docs.docker.com/engine/install/ubuntu/)

Docker version 20.10.16, build aa7e414

2. setup ssh keys access in your gitlab [see](https://docs.gitlab.com/ee/user/ssh.html#add-an-ssh-key-to-your-gitlab-account)

![image](https://gitlab.com/frontware_International/Odoo/royisal/uploads/90bac020a6de5b1c1bfcdebabe5a6109/image.png)

Testing with this command

```
    ssh -T git@gitlab.com
```

## Usage

### build

```
docker compose build --ssh default

```

### run

```
    docker compose up
```
