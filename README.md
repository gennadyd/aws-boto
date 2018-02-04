# aws-boto
Usage : 

../createNew.py --help </br>
usage: createNew.py [-h] --env_name ENV_NAME --elb_name ELB_NAME --action ACTION [--num_of_instances NUM_OF_INSTANCES] 


Build new envinronment including one Elastic Load Balancer (ELB) with num of EC2 instances (2 by default) </br>

optional arguments:
  -h, --help            show this help message and exit </br>
  --env_name ENV_NAME   the environment name  </br>
  --elb_name ELB_NAME   the loadbalancer name </br>
  --action ACTION       The action to take (e.g. create,destroy,stop,start) </br>
  --num_of_instances NUM_OF_INSTANCES </br>
                        Optional : set number of instances to build and assign to ELB (2 by default) </br>

--- create new environment  </br>
./createNew.py  --env_name Prod --elb_name newSite --action create </br>

--- destroy environment  </br>
./createNew.py  --env_name Prod --elb_name newSite --action destroy 




