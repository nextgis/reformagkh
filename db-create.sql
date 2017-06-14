; create and initialize PostgreSQL database
; must be run as a 'postgres' user

create role gkh with login createdb encrypted password 'gkh';
create database gkh01 owner 'gkh';
\c gkh01
create extension postgis;
