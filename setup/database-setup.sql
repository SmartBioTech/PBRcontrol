create user if not exists 'PBRcontrol'@'localhost';
create database if not exists localdb;
grant all privileges on localdb.* to 'PBRcontrol'@'localhost' identified by '';