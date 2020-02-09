#!/usr/bin/env bash

# **prepare_swift.sh**
#
# Install all swift components.
#
# prepare_swift.sh <build_number>

# Define variables
ELOS_PACKAGE_URL=http://scae12sn-fe.us.oracle.com/shares/export/automation/exalogic_openstack/wheels

# Create a temporary folder and download the ELOS package
BUILD_NUMBER=$1
TEMP_FOLDER=`mktemp -d`
echo "Temporary folder $TEMP_FOLDER has been created."
PKG_FILE_NAME=hudson-openstack_build_wheels-$BUILD_NUMBER.tar.gz
LOCAL_PKG_FILE_NAME=$TEMP_FOLDER/elos-$BUILD_NUMBER.tar.gz

wget -q $ELOS_PACKAGE_URL/$BUILD_NUMBER/$PKG_FILE_NAME \
         -O $LOCAL_PKG_FILE_NAME
tar -xf $LOCAL_PKG_FILE_NAME -C $TEMP_FOLDER

# Install prereqs for swift
pushd $TEMP_FOLDER/prereqs
source $TEMP_FOLDER/prereqs/install_swift_prereqs.sh
popd