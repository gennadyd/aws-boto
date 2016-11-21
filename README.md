# aws-boto
1. Define Objects for a cluster of:
  a. ELB (Elastic Load Balancer)
  b. n EC2 instances (2 by default, but any amount in general)

2. Create CLI usage that would accept whatever arguments you may need. Please support '--help' and clear error messages. It should support '--create' and '--destroy' with whatever parameters you may need.

3. The code should use the 'boto' library for working with AWS.

4. The code should use predefined AWS credentials (API/SSH). Can be hard coded. As well as the shell commands for the work on the server.

5. The script should spin up the resources, install the web servers, connect them to the ELB, and validate it's working (no need to retry, simply quit on failures).

6. The EC2 instances should have a web server running on them and return some unique data from the default path (e.g. /index.html should return the AWS Instance ID and internal IP address)

7. The output of the script should be the DNS address of the ELB and the result of 5 GET requests to the default path.



Usage : 

--- create new environment 
./createNew.py  --env_name Prod --elb_name newSite --action create

-- destroy environment 
./createNew.py  --env_name Prod --elb_name newSite --action destroy

