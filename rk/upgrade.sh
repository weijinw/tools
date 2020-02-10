#!/bin/sh

build_number=$1
version="5.3~dev"
cluster="1416"

cdm_bld_url="http://cdm-builds.corp.rubrik.com/view/all/job/Build_CDM"
if [ -z "$build_number" ]; then
	echo "./upgrade <build-number>"
	exit 1
fi

echo "build number: $build_number"


echo "downloading packages ..."
rk_pkg="rubrik-$version-$build_number.tar.gz"
internal_rk_pkg="internal-rubrik-$version-$build_number.tar.gz"
rk_tar=$cdm_bld_url/$build_number/artifact/$rk_pkg
rki_tar=$cdm_bld_url/$build_number/artifact/$internal_rk_pkg
echo "wget $rk_tar"
echo "wget $rki_tar"

wget $rk_tar
wget $rki_tar

echo "unzip the packages ..."
tar xfz $rk_pkg
tar xfz $internal_rk_pkg -C rubrik-$version-$build_number --strip-components=1

echo "copy the cluster configurations for $cluster ..."
cp ./conf/*$cluster* ./rubrik-$version-$build_number/conf/
cp ./ansible/*$cluster* ./rubrik-$version-$build_number/deployment/ansible/

i=`cat conf/*cluster* | grep _ipv6 | awk '{ print $2 }'`
echo "Start to upgrade $i to build $build_number"

echo "run below command in a docker container:"
echo "   UPGRADE_CHECK=0 nohup ./deployment/cluster.sh $i upgrade &"
#UPGRADE_CHECK=0 nohup ./deployment/cluster.sh $i upgrade &