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
     --region RegionDevstack  \
     --publicurl 'http://10.160.25.120:8774/v2/$(tenant_id)s'  \
     --adminurl 'http://10.160.25.120:8774/v2/$(tenant_id)s' \
     --internalurl 'http://10.160.25.120:8774/v2/$(tenant_id)s' \
  nova

openstack endpoint create \
     --region RegionDevstack  \
     --publicurl 'http://10.160.25.120:8774/v2.1/$(tenant_id)s'  \
     --adminurl 'http://10.160.25.120:8774/v2.1/$(tenant_id)s' \
     --internalurl 'http://10.160.25.120:8774/v2.1/$(tenant_id)s' \
  nova21

# glance
openstack endpoint create \
     --region RegionDevstack  \
     --publicurl 'http://10.160.25.120:9292'  \
     --adminurl 'http://10.160.25.120:9292' \
     --internalurl 'http://10.160.25.120:9292' \
  glance

#cinder
openstack endpoint create \
     --region RegionDevstack  \
     --publicurl 'http://10.160.25.120:8776/v1/$(tenant_id)s'  \
     --adminurl 'http://10.160.25.120:8776/v1/$(tenant_id)s' \
     --internalurl 'http://10.160.25.120:8776/v1/$(tenant_id)s' \
  cinder

#cinderv2
openstack endpoint create \
     --region RegionDevstack  \
     --publicurl 'http://10.160.25.120:8776/v2/$(tenant_id)s'  \
     --adminurl 'http://10.160.25.120:8776/v2/$(tenant_id)s' \
     --internalurl 'http://10.160.25.120:8776/v2/$(tenant_id)s' \
  cinderv2

# ec2
openstack endpoint create \
     --region RegionDevstack  \
     --publicurl 'http://10.160.25.120:8773/'  \
     --adminurl 'http://10.160.25.120:8773/' \
     --internalurl 'http://10.160.25.120:8773/'10.160.25.120 \
  ec2