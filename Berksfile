source "https://supermarket.chef.io"

cookbook 'apache2', '3.0.0'
cookbook 'apt', '2.6.1'
cookbook 'aws', '2.1.1'
cookbook 'build-essential', '1.4.2'
cookbook 'ceph', '0.8.0'
cookbook 'database', '4.0.2'
cookbook 'erlang', '1.4.2'
cookbook 'memcached', '1.7.2'
cookbook 'mysql', '6.0.13'
cookbook 'mysql2_chef_gem', '1.0.1'
cookbook 'openssl', '4.0.0'
cookbook 'postgresql', '3.4.18'
cookbook 'python', '1.4.6'
cookbook 'rabbitmq', '3.9.0'
cookbook 'xfs', '1.1.0'
cookbook 'yum', '3.5.2'
cookbook 'selinux', '0.7.2'
cookbook 'yum-epel', '0.6.0'

%w{block-storage common compute
   dashboard database identity image
   network}.each do |cookbook|
  if ENV['REPO_DEV'] && Dir.exist?("../cookbook-openstack-#{cookbook}")
    cookbook "openstack-#{cookbook}", path: "../cookbook-openstack-#{cookbook}"
  else
    cookbook "openstack-#{cookbook}", github: "openstack/cookbook-openstack-#{cookbook}"
  end
end
