create user if not exists 'PBRcontrol'@'localhost' identified by '&Bioarineo1';
create database if not exists localdb;
grant all privileges on localdb.* to 'PBRcontrol'@'localhost' identified by '&Bioarineo1';