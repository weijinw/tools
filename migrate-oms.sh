#!/bin/sh

PSQL="/opt/vmware/vpostgres/current/bin/psql"

function help() {
   echo "Migrate the data from another oms server to current oms server."
   echo "  $0  <IP> username password"
   echo "      username can only be root now."
}

function add_authorized_key() {
   echo "Add key to $1"
   mkdir -P /root/.ssh
   cp /home/viouser/.ssh/* /root/.ssh
   ssh $2@$1 'mkdir -P /root/.ssh'
   cat /root/.ssh/id_rsa.pub | ssh $2@$1 'cat >> /root/.ssh/authorized_keys'
   ssh $2@$1 'pwd'
   echo "Done!"
}

function stop_oms_and_osvmw_remotely() {
   echo "Stop oms service and osvmw service on $1..."
   ssh $2@$1 'stop oms && stop osvmw'
   echo "Done!"
}

function stop_oms_and_osvmw() {
   echo "Stop oms service and osvmw service..."
   stop oms
   stop osvmw
   echo "Done!"
}

function start_oms_and_osvmw() {
   echo "Start oms service and osvmw service..."
   start oms
   start osvmw
   echo "Done!"
}

function dump_database() {
   echo "Dump $3 to /tmp/$3"
   ssh $2@$1 "/opt/vmware/vpostgres/current/bin/pg_dump -U $3  omsdb > /tmp/$3"
   echo "Done!"
}

function restore_database() {
   echo "Restore $1 from $2"
   PSQL -U $1 -d postgres -c "DROP DATABASE $1;"
   PSQL -U omsdb -d postgres -c "CREATE DATABASE $1 WITH OWNER = omsdb ENCODING = 'UTF-8' TEMPLATE template0;"
   PSQL -U omsdb omsdb < $2
   echo "Done!"
}

function update_property() {
   # host username file key
   echo "Get property $4 from $3 in server $1, and update the file locally..."
   key_value_pair=$(ssh $2@$1 "cat $3 | grep $4")
   sed -i "s/$4=.*$/$key_value_pair/" $3
   echo "Done!"
}

function scp_file() {
   echo "Copy file $2 from $1"
   scp $2@$1:$3 $3
   echo "Done!"
}

function scp_folder() {
   echo "Copy folder $2 from $1"
   scp -r $2@$1:$3 $3
   echo "Done!"
}

function chown_file() {
   echo "chown $1 $2"
   chown $1 $2
   echo "Done!"
}

function chown_folder() {
   echo "chown $1 $2"
   chown -R $1 $2
   echo "Done!"
}

USERNAME="root"
PASSWORD="vmware"

if [ "$#" -lt 1 ] ; then
   help
else
   if [ -z "$2+x" ]; then
      USERNAME=$2
   fi
   
   if [ -z "$3+x" ]; then
      PASSWORD=$3
   fi
   
   HOST=$1
   echo "Migrate data from $HOST, username=$USERNAME, password=$PASSWORD."

   # Remote server
   #add_authorized_key $HOST $USERNAME $PASSWORD
   stop_oms_and_osvmw_remotely $HOST $USERNAME
   dump_database $HOST $USERNAME "omsdb"
   dump_database $HOST $USERNAME "osvmwplugindb"

   # local vm
   stop_oms_and_osvmw
   scp_file $HOST $USERNAME "/tmp/omsdb"
   scp_file $HOST $USERNAME "/tmp/osvmwplugindb"

   restore_database "omsdb" "/tmp/omsdb"
   restore_database "osvmwplugindb" "/tmp/osvmwplugindb"

   scp_file $HOST $USERNAME "home/viouser/.ssh/id_rsa"
   scp_file $HOST $USERNAME "home/viouser/.ssh/id_rsa.pub"
   chown_file viouser:viogrp "home/viouser/.ssh/*"

   scp_file $HOST $USERNAME "home/jarvis/.ssh/id_rsa"
   scp_file $HOST $USERNAME "home/jarvis/.ssh/id_rsa.pub"
   chown_file jarvis:viogrp "home/jarvis/.ssh/*"

   scp_file $HOST $USERNAME "home/omsapp/.ssh/id_rsa"
   scp_file $HOST $USERNAME "home/omsapp/.ssh/id_rsa.pub"
   chown_file omsapp:viogrp "home/omsapp/.ssh/*"

   scp_file $HOST $USERNAME "/opt/vmware/vio/etc/guard.key"
   chown_file omsapp:viogrp "/opt/vmware/vio/etc/guard.key"
   update_property $HOST $USERNAME "/opt/vmware/vio/etc/vio_system.properties" "cms.guard_keystore_pswd"

   scp_file $HOST $USERNAME "/var/lib/vio/ansible/vault/vault_pass.txt"
   chown_file jarvis:viogrp "/var/lib/vio/ansible/vault/vault_pass.txt"

   scp_folder $HOST $USERNAME "/var/lib/vio/jarvis"
   chown_folder jarvis:viogrp "/var/lib/vio/jarvis"

   start_oms_and_osvmw
fi
