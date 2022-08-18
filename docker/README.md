# Royisal docker for developer

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

### at first run

run this 

```
docker exec -u root -it royisal-odoo14 chown odoo /mnt/odoo14 -R
```

### after restore db from customer

run this 

```
docker exec -e PGPASSWORD=odoo -it docker-db-1 psql **yourdb** -c 'delete from ir_mail_server;delete from fetchmail_server;' -U odoo
```
### problems after restore db

#### 
column res_company.no_space_title_name does not exist

```
docker exec -e PGPASSWORD=odoo -it docker-db-1 psql dev20220609 -c 'alter table res_company add column no_space_title_name char;' -U odoo
```

column stock_picking_type.bypass_wa does not exist
```
docker exec -e PGPASSWORD=odoo -it docker-db-1 psql dev20220609 -c 'alter table stock_picking_type add column bypass_wa bool;' -U odoo
```

column res_partner.purchase_incoterm_address_id does not exist
```
docker exec -e PGPASSWORD=odoo -it docker-db-1 psql dev20220609 -c 'alter table res_partner add column purchase_incoterm_address_id int;' -U odoo
```

External ID not found in the system: rma.group_rma_manual_finalization

![image](https://gitlab.com/frontware_International/Odoo/royisal/uploads/0f8ec8f685cb905fdd4296a9717dc89f/image.png)
