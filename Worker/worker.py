import pika
import time
import json
import pymongo
import bson
import hashlib
import configparser
from elasticsearch import Elasticsearch

# Initializing configurations
config = configparser.ConfigParser()
config.read('config.ini')
es     = Elasticsearch({'elasticsearch'})


# Handling JSON data received in request
def handleRequest(msgJSON):
    client  = pymongo.MongoClient(config['DB']['dbUrl'])
    logsDb  = client["trogsDb"]["logs"]
    usersDb = client["trogsDb"]["users"]

    merchant=re.findall("(.*?)\--",a)
    merchant=merchant[0]
    # Currently hard coded for testing
    title    = "Testing log title: " + msgJSON['logData'][0:6]
    amount   = 1000
    msgRefId = "123456789"
    category = "Bank"
    parse = dataSms(msgJSON['logData'],merchant);
    if len(parse)==0:
        return;
    if parse.spamval==1:
        return;
    boolPersonal = True if msgJSON['boolPersonal'] == "true" else False
    newId        = bson.objectid.ObjectId()
    uniqRefId    = hashlib.sha3_224(str(newId).encode('utf-8')).hexdigest()
    userLogs     = msgJSON['userLogs'] if msgJSON['userLogs'] is not None else []
    userLogs.append(uniqRefId)
    saveLogData  = {
        '_id'         : newId,
        'uniqRefId'   : uniqRefId,
        'completeLog' : msgJSON['logData'],
        'boolPersonal': boolPersonal,
        'genUserId'   : msgJSON['uid'],
        'secUsername' : msgJSON['secUsername'],
        'title'       : title,
        'amount'      : parse.amount,
        'msgRefId'    : parse.transNo,
        'category'    : parse.category
    }
    newLogData  = {
        'uniqRefId'   : uniqRefId,
        'completeLog' : msgJSON['logData'],
        'boolPersonal': boolPersonal,
        'genUserId'   : msgJSON['uid'],
        'secUsername' : msgJSON['secUsername'],
        'title'       : title,
        'amount'      : amount,
        'msgRefId'    : msgRefId,
        'category'    : category
    }

    result1 = logsDb.insert_one(saveLogData)
    result2 = usersDb.update_one({"uid": msgJSON['uid']}, {"$set" : {"logs": userLogs} })
    res     = es.index(index='logss',doc_type='Logs',body=newLogData)
    print(res['created'])

def dataSms(a,merchant):
        amt=re.findall("[rR][sS]\.?\s[,\d]+\.?\d{0,2}|[iI][nN][rR]\.?\s*[,\d]+\.?\d{0,2}",a)
        spam=re.search("(offer|promo|discount)",a)
        spamval=0
        if spam:
                spamval=1
        if spamval==1:
                return {}
        transNo=re.findall("((UPI Ref No|No|Txn|Txn#|txn#|txn)\s*[0-9]+)",a);
        debval=0;
        credval=0;
        typDebit=re.search(".debit.",a)
        if typDebit:
                debval=1
        typCredit=re.search(".credit.",a)
        if typCredit:
                credval=1
        dict={"merchantName":merchant,"amount":amt,"spamStatus":spamval,"transNo":transNo[0][0],"Debit":debval,"Credit":credval,"body":a,"category":"bank"}
        emp={};
        typWallet=re.search("(wallet|Wallet)",a);
        if typWallet:
                wallet=1
        print(wallet)
        if debval==1 or credval==1:
                return dict
        elif wallet==1:
                typDebit=0
                typCredit=0
                typDebit=re.search(".(paid|deducted).",a)
                print(typDebit)
                if typDebit:
                        debval=1
                typCredit=re.search(".(added|received).",a)
                if typCredit:
                        credval=1
                dict={"merchantName":merchant,"amount":amt,"spamStatus":spamval,"transNo":transNo[0][0],"Debit":debval,"Credit":credval,"body":a,"category":"wallet"}
                return dict
        else:
                 return emp;

# Function called as soon as message received from queue
def callback(ch, method, properties, body):
    msgJSON = json.loads(body)
    handleRequest(msgJSON)
    ch.basic_ack(delivery_tag = method.delivery_tag)

# Connect to Rabbitmqserver and create a channel
connection = pika.BlockingConnection(pika.ConnectionParameters(host='dockerdbsetup_messagebroker_1'))
channel = connection.channel()

# Declaring queue with durability enabled
channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

# For load balancing
channel.basic_qos(prefetch_count=1)

# Start consuming requests from broker
channel.basic_consume(on_message_callback=callback, queue='task_queue')
channel.start_consuming()
