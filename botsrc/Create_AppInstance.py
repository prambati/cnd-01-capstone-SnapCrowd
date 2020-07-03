from datetime import datetime
import logging
import json
import sys

import boto3
import botocore

cf = boto3.client('cloudformation')
client = boto3.client('s3')


def create_instance(instance_type):
    
    log = logging.getLogger('connecting to S3 to read cloud formation templare')
    BUCKET = 'cnd-project-sc-store'
    FILE_TO_READ = 'cf-templates/EC2HealthStack.json'
    result = client.get_object(Bucket=BUCKET,Key=FILE_TO_READ)
    stack_template=result["Body"].read().decode()
    log = logging.getLogger('got the required template from S3')
    
    log = logging.getLogger('connecting to S3 to read parameter template')
    BUCKET = 'cnd-project-sc-store'
    FILE_TO_READ = 'cf-templates/'+instance_type+'.json'
    result = client.get_object(Bucket=BUCKET,Key=FILE_TO_READ)
    param_template=result["Body"].read().decode()
    log = logging.getLogger('got the required template from S3')
    
    
    template_data = _parse_template(stack_template)
    parameter_data = _parse_template(param_template)

    params = {
        'StackName': instance_type,
        'TemplateBody': template_data,
        'parameter': parameter_data,
    }

    try:
        if _stack_exists(stack_name):
            print('Updating {}'.format(stack_name))
            stack_result = cf.update_stack(**params)
            waiter = cf.get_waiter('stack_update_complete')
        else:
            print('Creating {}'.format(stack_name))
            stack_result = cf.create_stack(**params)
            waiter = cf.get_waiter('stack_create_complete')
        print("...waiting for stack to be ready...")
        waiter.wait(StackName=stack_name)
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print("No changes")
        else:
            raise
   
        
    response = cf_client.describe_stacks(StackName=instance_type)
    
    if outputs is not None:
            outputs = response["Stacks"][0]["Outputs"]
            for output in outputs:
                keyName = output["OutputKey"]
                if keyName == "EC2APPURL":
                    return output["OutputValue"]
                else:
                    return "Error while getting outputs"
    else:
        return "Unable to create instance"
                
    


def _parse_template(template):
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
    cf.validate_template(TemplateBody=template_data)
    return template_data


def _parse_parameters(parameters):
    with open(parameters) as parameter_fileobj:
        parameter_data = json.load(parameter_fileobj)
    return parameter_data


def _stack_exists(stack_name):
    stacks = cf.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True
    return False


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")
    