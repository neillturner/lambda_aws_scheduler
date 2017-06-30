# lambda_aws_scheduler

Stop and start server instances according to schedule via lambda and terraform

## Prerequisites

* Terraform 

* Python 2.x. For windows need a python env installed as per 

http://www.tylerbutler.com/2012/05/how-to-install-python-pip-and-virtualenv-on-windows-with-powershell/

* For Windows: a bash client to run deploy.sh (can get from git for windows ) 


## Install

* in a command windows go to the directory

* ./deploy.sh       (builds the zip file for lambda)

* terraform apply   (run terraform to deploy)


## Options

* if you set the code 'create_schedule_tag_force = True' in the 'aws-scheduler.py' script it with create a default schedule tag for each instance it finds.

* Other options are in the 'aws-scheduler.cfg' file.

* time can be local or gmt.

## Usage

* It works by setting a tag (default name schedule) to a json string giving the stop and start time hour for each day.
