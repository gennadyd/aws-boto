# aws-boto
Usage : 

../createNew.py --help
usage: createNew.py [-h] --env_name ENV_NAME --elb_name ELB_NAME --action ACTION [--num_of_instances NUM_OF_INSTANCES]

Build new envinronment including one Elastic Load Balancer (ELB) with num of EC2 instances (2 by default)

optional arguments:
  -h, --help            show this help message and exit
  --env_name ENV_NAME   the environment name
  --elb_name ELB_NAME   the loadbalancer name
  --action ACTION       The action to take (e.g. create,destroy,stop,start)
  --num_of_instances NUM_OF_INSTANCES
                        Optional : set number of instances to build and assign to ELB (2 by default)

--- create new environment 
./createNew.py  --env_name Prod --elb_name newSite --action create

--- destroy environment 
./createNew.py  --env_name Prod --elb_name newSite --action destroy




