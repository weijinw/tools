#!/bin/bash


# Set hostname
# ==================================
OLD_HOSTNAME="$( hostname )"
NEW_HOSTNAME="$1"

if [ -z "$NEW_HOSTNAME" ]; then
 echo -n "Please enter new hostname: "
 read -e NEW_HOSTNAME
fi

if [ -z "$NEW_HOSTNAME" ]; then
 echo "Error: no hostname entered. Exiting."
 exit 1
fi

echo "Changing hostname from $OLD_HOSTNAME to $NEW_HOSTNAME..."

hostname "$NEW_HOSTNAME"

sudo sed -i "s/$OLD_HOSTNAME/$NEW_HOSTNAME/g" /etc/hostname

if [ -n "$( grep "$OLD_HOSTNAME" /etc/hosts )" ]; then
 sudo sed -i "s/$OLD_HOSTNAME/$NEW_HOSTNAME/g" /etc/hosts
else
 sudo echo -e "$( hostname -I | awk '{ print $1 }' )\t$NEW_HOSTNAME" >> /etc/hosts
fi

echo "Changed hostname from $OLD_HOSTNAME to $NEW_HOSTNAME..."

# clone the devstack code
git clone https://git.openstack.org/openstack-dev/devstack

# prepare all the confs
cd ~/devstack
wget https://raw.githubusercontent.com/weijinw/tools/master/local.conf

# stack ....
./clean.sh
./stack.sh

echo "Done."
