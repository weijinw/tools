#!/bin/bash

echo $OS_USERNAME
echo $OS_PASSWORD
echo $OS_AUTH_URL

echo $KEYSTONE_SERVICE_HOST

openstack endpoint create \
     --region RegionTwo  \
     --publicurl 'http://$KEYSTONE_SERVICE_HOST:5000/v2.0'  \
     --adminurl 'http://$KEYSTONE_SERVICE_HOST:35357/v2.0' \
     --internalurl 'http://$KEYSTONE_SERVICE_HOST:5000/v2.0' \
  keystone
 
openstack endpoint create \
     --region RegionTwo  \
     --publicurl 'http://192.168.1.109:8774/v2/$(tenant_id)s'  \
     --adminurl 'http://192.168.1.109:8774/v2/$(tenant_id)s' \
     --internalurl 'http://192.168.1.109:8774/v2/$(tenant_id)s' \
  nova

openstack endpoint create \
     --region RegionTwo  \
     --publicurl 'http://192.168.1.109:8774/v2.1/$(tenant_id)s'  \
     --adminurl 'http://192.168.1.109:8774/v2.1/$(tenant_id)s' \
     --internalurl 'http://192.168.1.109:8774/v2.1/$(tenant_id)s' \
  nova21

# ec2
openstack endpoint create \
     --region RegionTwo  \
     --publicurl http://192.168.1.109:8773/  \
     --adminurl http://192.168.1.109:8773/ \
     --internalurl http://192.168.1.109:8773/ \
  ec2

# glance
openstack endpoint create \
     --region RegionTwo  \
     --publicurl http://192.168.1.109:9292  \
     --adminurl http://192.168.1.109:9292 \
     --internalurl http://192.168.1.109:9292 \
  glance

#cinder
openstack endpoint create \
     --region RegionTwo  \
     --publicurl 'http://192.168.1.109:8776/v1/$(tenant_id)s'  \
     --adminurl 'http://192.168.1.109:8776/v1/$(tenant_id)s' \
     --internalurl 'http://192.168.1.109:8776/v1/$(tenant_id)s' \
  cinder

#cinderv2
openstack endpoint create \
     --region RegionTwo  \
     --publicurl 'http://192.168.1.109:8776/v2/$(tenant_id)s'  \
     --adminurl 'http://192.168.1.109:8776/v2/$(tenant_id)s' \
     --internalurl 'http://192.168.1.109:8776/v2/$(tenant_id)s' \
  cinderv2