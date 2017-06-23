from ConfigParser import SafeConfigParser
import boto3 

import sys,os,json,logging, datetime, time
 
config = SafeConfigParser()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

aws_access_key = None
aws_secret_key = None
aws_region     = None

create_schedule_tag_force = False
 
def init():
    # Setup AWS connection
    aws_access_key = ""
    aws_secret_key = ""
    aws_region     = os.getenv('AWS_DEFAULT_REGION', '')
 
    global ec2
    if aws_access_key != '':
        logger.info("-----> Connecting using aws access and secret keys to region \"%s\"", aws_region)
        ec2 = boto3.client('ec2',
              region_name = aws_region,
              aws_access_key_id = aws_access_key,
              aws_secret_access_key = aws_secret_key)
    else:
        logger.info("-----> Connecting to region \"%s\"", aws_region)
        ec2 = boto3.resource('ec2', region_name=aws_region)

def get_with_default(section,name,default):
    return config.get(section,name) if config.has_section(section) and config.has_option(section, name) else default
 
#
# Add default 'schedule' tag to instance.
# (Only if instance.id not excluded and create_schedule_tag_force variable is True. 
#
def create_schedule_tag(instance):
    exclude_list = config.get("schedule","exclude")
 
    if (create_schedule_tag_force) and (instance.id not in exclude_list):
        try: 
            schedule_tag = config.get('schedule','tag','schedule')
            tag_value = config.get("schedule","default")
            logger.info("About to create %s tag on instance %s with value: %s" % (schedule_tag,instance.id,tag_value))
            tags = [{
	        "Key" : schedule_tag, 
	        "Value" : tag_value
            }] 
            instance.create_tags(Tags=tags)
        except Exception as e:
            logger.error("Error adding Tag to instance: %s" % e)
    else:
        logger.info("No 'schedule' tag found on instance %s. Use -force to create the tag automagically" % instance.id)
 
#
# Loop EC2 instances and check if a 'schedule' tag has been set. Next, evaluate value and start/stop instance if needed.
#
def check():
    # Get all reservations.
    instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['pending','running','stopping','stopped']}])
  
    # Get current day + hour (using GMT by defaul if time parameter not set to local)
    time_zone = config.get("schedule","time")
    if time_zone == 'local':
        hh  = int(time.strftime("%H", time.localtime()))
        day = time.strftime("%a", time.localtime()).lower()
        logger.info("-----> Checking for instances to start or stop for 'local time' hour \"%s\"", hh)
    else:
        hh  = int(time.strftime("%H", time.gmtime()))
        day = time.strftime("%a", time.gmtime()).lower()
        logger.info("-----> Checking for instances to start or stop for 'gmt' hour \"%s\"", hh)

    started = []
    stopped = []
 
    schedule_tag = config.get('schedule','tag','schedule')
    logger.info("-----> schedule tag is called \"%s\"", schedule_tag)
    for instance in instances:
        logger.info("Evaluating instance \"%s\"", instance.id)
 
        try:
            data = "{}"
            for tag in instance.tags:
	        if schedule_tag in tag['Key']:
                    data = tag['Value']
                    break
	    else:
            	# 'schedule' tag not found, create if appropriate.
            	create_schedule_tag(instance)
                
            schedule = json.loads(data)

            try:
            	if hh == schedule[day]['start'] and not instance.state["Name"] == 'running':
            	    logger.info("Starting instance \"%s\"." %(instance.id))
            	    started.append(instance.id)
            	    ec2.instances.filter(InstanceIds=[instance.id]).start()
            except:
                pass # catch exception if 'start' is not in schedule.
 
            try:
            	if hh == schedule[day]['stop']:
            	    logger.info("Stopping time matches")
            	if hh == schedule[day]['stop'] and instance.state["Name"] == 'running':
            	    logger.info("Stopping instance \"%s\"." %(instance.id))
            	    stopped.append(instance.id)
            	    ec2.instances.filter(InstanceIds=[instance.id]).stop()
            except:
                pass # catch exception if 'stop' is not in schedule.
 

        except ValueError as e:
            # invalid JSON
            logger.error('Invalid value for tag \"schedule\" on instance \"%s\", please check!' %(instance.id))
                
                
# Main function. Entrypoint for Lambda
def handler(event, context):

    config.read(os.environ['LAMBDA_TASK_ROOT']+'/aws-scheduler.cfg')

    init()
 
    check()
 
# Manual invocation of the script (only used for testing)
if __name__ == "__main__":
    # Test data
    test = {}
    handler(test, None)
