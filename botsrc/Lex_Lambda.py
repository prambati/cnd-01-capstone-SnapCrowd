import json
import csv
import boto3
import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging
import create_instance

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    return response

""" --- Function that return employee name --- """

def select_instance(instance_type):
    logger.debug(instance_type)
    
    if not instance_type:
        apptype =  create_instance(instance_type)
    
    else:
        return ('Please select one application, which you are looking for health info app, health care app, health medical app ')
        
def return_instance(intent_request):
    """
    Performs dialog management and fulfillment for returning employee's department Name.
    """
    instance = intent_request['currentIntent']['slots']['instance']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        slots = intent_request['currentIntent']['slots']
    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Hello! {}'.format(select_instance(instance))
        }
    )

""" --- Intents --- """
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    logger.debug('dispatch intentName={}'.format(intent_request['currentIntent']['name']))
    
    intent_name = intent_request['currentIntent']['name']
    
    # Dispatch to your bot's intent handlers
    if intent_name == 'testhealth':
        return return_instance(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')

""" --- Main handler --- """
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)