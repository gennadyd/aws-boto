#!/usr/bin/python
import sys
import time
import boto.ec2.connection
import boto.ec2.elb
import boto.ec2

import argparse
from argparse import RawTextHelpFormatter

import logging

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


###############################################################################################################################################
class env_class(object):
    def __init__(self, name, elb_name):
        # LOG.info ("ENV constructor")
        self.env_name = name
        self.elb_name = elb_name
        self.instance_id = instance_id

    def create(self):
        """
        Create new ENV
        """
        elb_o = elb_class(name, elb_name, instance_id, num_of_instances)
        elb_o.create()

    def destroy(self):
        """
        Destroy ENV
        """
        instance_name = ""
        ec2_o = ec2_class(name, elb_name, instance_id, instance_name)
        elb_hosts = ec2_o.get_instances()
        ec2_o.destroy(elb_hosts[2])
        elb_o = elb_class(name, elb_name, instance_id, num_of_instances)
        elb_o.destroy()

    def start(self):
        """
        Start ENV
        """
        LOG.info("Start ENV")
        instance_name = ""
        ec2_o = ec2_class(name, elb_name, instance_id, instance_name)
        elb_hosts = ec2_o.get_instances()
        ec2_o.start(elb_hosts[1])

    def stop(self):
        """
        Stop ENV
        """
        LOG.info("Stop ENV")
        instance_name = ""
        ec2_o = ec2_class(name, elb_name, instance_id, instance_name)
        elb_hosts = ec2_o.get_instances()
        ec2_o.stop(elb_hosts[0])


###############################################################################################################################################
class elb_class(env_class):
    def __init__(self, name, elb_name, instance_id, num_of_instances):
        # LOG.info ("ELB constructor")
        super(elb_class, self).__init__(name, elb_name)
        self.num_of_instances = num_of_instances
        self.instance_id = instance_id

    def get_conn(self):
        """
        Connect to ELB
        """
        LOG.info("Get connection to ELB")
        region = "us-west-2"
        aws_access_key_id = 'aws_key'
        aws_secret_access_key = 'aws_key_secret'
        try:
            elbc = boto.ec2.elb.connect_to_region(region, aws_access_key_id=aws_access_key_id,
                                                  aws_secret_access_key=aws_secret_access_key)
        except Exception:
            LOG.error("Failed connect to ELB")
            return False
        LOG.info("Connected to ELB %s", elbc)
        return elbc

    def get_elb(self, elb_name):
        """
        Get ELB by name.
        """
        LOG.info("Get ELB by elb_name %s", elb_name)
        try:
            elbc = self.get_conn()
            lb = elbc.get_all_load_balancers(elb_name)[0]

        except Exception:
            LOG.error("Failed to find ELB: %s", elb_name)
            return False
        LOG.info("Connected to ELB Name %s", elb_name)
        return lb

    def create(self):
        """
        Create new ELB
        """
        LOG.info("Create new ELB %s", elb_name)
        try:
            elbc = self.get_conn()
            elb_security_groups = ['elbSecurityGroup']
            new_lb = elbc.create_load_balancer(
                name=elb_name,
                listeners=[(80, 80, 'http')],
                zones=['us-west-2b', 'us-west-2a']
            )
            instance_ids = []
            for i in range(num_of_instances):
                instance_name = "%s_%s_%s" % (name, elb_name, i)
                ec2_o = ec2_class(name, elb_name, instance_id, instance_name)
                new_instance_id = ec2_o.create()
                LOG.info("new_instance_id return %s", new_instance_id)
                instance_ids.append(new_instance_id)
                self.join(instance_ids)
        except Exception:
            LOG.error("Can not create new ELB: %s", elb_name)
            return False
        LOG.info("New ELB %s created", elb_name)
        return new_lb, instance_ids

    def destroy(self):
        """
        Destroy ELB by name
        """
        LOG.info("Destroy ELB %s", elb_name)
        try:
            elbc = self.get_conn()
            elbc.delete_load_balancer(name=elb_name)
        except Exception:
            LOG.error("Can not destroy ELB %s", elb_name)
            return False
        LOG.info("ELB %s destroyed", elb_name)
        return True

    def join(self, instance_id):
        """
        Assign instance to ELB
        """
        LOG.info("Add instances %s to ELB %s", instance_id, elb_name)
        lb = self.get_elb(elb_name)
        try:
            lb.register_instances(instance_id)
        except Exception:
            LOG.error("Error while registering instance %s to %s", instance_id, elb_name)
            return False
        LOG.info("Instance_Id %s registered to ELB %s", instance_id, elb_name)
        return True


###############################################################################################################################################
class ec2_class(env_class):
    def __init__(self, name, elb_name, instance_id, instance_name):
        # LOG.info ("EC2 constructor" )
        super(ec2_class, self).__init__(name, elb_name)
        self.instance_name = instance_name
        self.instance_id = instance_id

    def get_conn(self):
        """
        Connect to the specified EC2 region using the given access key
        """
        LOG.info("Get connection to EC2")
        region = "us-west-2"
        aws_access_key_id = 'aws_key'
        aws_secret_access_key = 'aws_key_secret'
        try:
            ec2c = boto.ec2.connect_to_region(region, aws_access_key_id=aws_access_key_id,
                                              aws_secret_access_key=aws_secret_access_key)
        except Exception:
            LOG.error("EC2: Failed connect to EC2")
        LOG.info("Connected to EC2 %s", ec2c)
        return ec2c

    def create(self):
        """
        Create new instance
        """
        LOG.info("Create new instance %s", self.instance_name)

        ec2_security_groups = ['mySecurityGroup']
        ec2c = self.get_conn()
        key_name = "myKeyPair"
        instance_type = "t2.micro"
        user_data_script = """#!/bin/bash
							echo 'start script' >> /tmp/user_data.log
							sudo yum install httpd -y
							sudo chmod a+w /var/www/html/
							sudo /opt/aws/bin/ec2-metadata -i >> /var/www/html/index.html
							sudo /opt/aws/bin/ec2-metadata -p >> /var/www/html/index.html
							sudo service httpd start
							
							"""

        ec2Machine = ec2c.run_instances('ami-b04e92d0',
                                        key_name=key_name,
                                        instance_type=instance_type,
                                        security_groups=ec2_security_groups,
                                        user_data=user_data_script)

        instance = ec2Machine.instances[0]

        # Check up on its status every so often
        status = instance.update()
        while status == 'pending':
            time.sleep(10)
            status = instance.update()

        if status == 'running':
            # tag = 
            instance.add_tag("Name", self.instance_name)
        else:
            print('Instance status: ' + status)
            return None

        LOG.info("Instance_Id %s created", str(instance.id))
        return instance.id

    def destroy(self, instance_ids):
        """
        Destroy instance by instance_ids
        """
        LOG.info("Destroy instance_id %s", str(instance_ids))
        try:
            ec2c = self.get_conn()
            ec2c.terminate_instances(instance_ids=instance_ids)
        except Exception:
            LOG.error("Can not terminate instance_ids %s", instance_ids)
            return False
        LOG.info("Instance_Id %s terminated", str(instance_ids))
        return True

    def start(self, instance_ids):
        """
        Start instance by instance_ids
        """
        LOG.info("Starting instance_id %s", str(instance_ids))
        try:
            ec2c = self.get_conn()
            ec2c.start_instances(instance_ids=instance_ids)
        except Exception:
            LOG.error("Can not start instance_ids %s", instance_ids)
            return False
        LOG.info("Instance_Id %s started", str(instance_ids))
        return True

    def stop(self, instance_ids):
        """
        Stop instance by instance_ids
        """
        LOG.info("Stoping instance_id %s", str(instance_ids))
        try:
            ec2c = self.get_conn()
            ec2c.stop_instances(instance_ids=instance_ids)
        except Exception:
            LOG.error("Can not stop instance_ids %s", instance_ids)
            return False
        LOG.info("Instance_Id %s stoped", str(instance_ids))
        return True

    def get_instances(self):
        """
        Get instances under ELB
        """
        LOG.info("Get all instatnces under ELB %s", elb_name)
        try:
            elb_o = elb_class(name, elb_name, instance_id, num_of_instances)
            elbc = elb_o.get_conn()
            lb = elbc.get_all_load_balancers(elb_name)[0]
            ec2c = self.get_conn()
            rs = ec2c.get_all_instances(instance_ids=map(lambda x: x.id, lb.instances))
            runnig_elb_hosts = []
            stopped_elb_hosts = []
            for r in rs:
                for i in r.instances:
                    if i.state != 'running':
                        stopped_elb_hosts.append(i.id)
                    else:
                        runnig_elb_hosts.append(i.id)

            all_elb_hosts = runnig_elb_hosts + stopped_elb_hosts
        except Exception:
            LOG.error("Can not get instances under ELB %s", elb_name)
            return False
        LOG.info("Following running instances %s , stopped instances %s were found under ELB %s", runnig_elb_hosts,
                 stopped_elb_hosts, elb_name)
        return runnig_elb_hosts, stopped_elb_hosts, all_elb_hosts


###############################################################################################################################################
if __name__ == "__main__":
    """
    Create help
    """
    parser = argparse.ArgumentParser(
        description='Build new envinroment including one Elastic Load Balancer (ELB) with num of EC2 instances (2 by default)',
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('--env_name', help='the environment name', required=True)
    parser.add_argument('--elb_name', help='the environment name', required=True)
    parser.add_argument('--action', help='The action to take (e.g. create,destroy,stop,start) ', required=True)
    parser.add_argument('--num_of_instancess', type=int,
                        help='number of instances to build and assign to ELB (2 by default)')

    args = parser.parse_args()
    name = args.env_name
    elb_name = args.elb_name
    action = args.action
    num_of_instances = args.num_of_instancess
    instance_id = []

    if not num_of_instances:
        num_of_instances = 2
        LOG.info("If num_of_instancess is not set. By default create %s instances", num_of_instances)
    env_o = env_class(name, elb_name)
    if action == 'create':
        print
        "Creating a environment ", name, ". Please wait"
        env_o.create()
        elb_o = elb_class(name, elb_name, instance_id, num_of_instances)
        lb_dns_name = "http://" + elb_o.get_elb(elb_name).dns_name
        print
        lb_dns_name
        import urllib2

        content = urllib2.urlopen(str(lb_dns_name)).read()
        print
        content
    elif action == 'destroy':
        print
        "Deleting environment ", name
        env_o.destroy()

    elif action == 'start':
        env_o.start()
    elif action == 'stop':
        env_o.stop()
    else:
        LOG.error("the action %s is not supported.", action)
