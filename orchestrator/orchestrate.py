import uuid, time, boto, json, sys
from boto.sqs.message import RawMessage
from datetime import datetime, date, time, timedelta

# AWSKey = "{redacted}"
# AWSSecret = "{redacted}"
# AWS credentials will come from ~/.aws or ~/.boto or Environment vars

# Connect to SQS and open the queue
def initQueue(queue_name):
    # sqs = boto.connect_sqs()
    conn = boto.sqs.connect_to_region("us-west-2")
    # queue = sqs.create_queue(queue_name)
    print "Attempting to connect to queue "+queue_name
    queue = conn.get_queue(queue_name)
    if queue is None:
        print "Connect failed."
        print conn.get_all_queues()
    return queue

# Pushes a message onto the queue
def addMessageToQueue(message, queue):
    # Data required by the API
    data = {
        'key': str(uuid.uuid1()),
        'date': str(message)
    }

    # Put the message in the queue
    m = RawMessage()
    m.set_body(json.dumps(data))
    status = queue.write(m)

def main(msgFn, queue, spec_file):
    with open(spec_file, "r") as myfile:
        data = myfile.read()
    spec = json.loads(data)
    start = datetime.strptime(spec['start_date'], "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(spec['end_date'], "%Y-%m-%d %H:%M:%S")
    count = spec['count']

    td = end - start
    delta_second = td.total_seconds() / count
    time_now = start
    td_incr = timedelta(seconds=delta_second) 
    for i in range(0, count):
        msg = time_now.strftime("%Y-%m-%d 00:00:00")
        msgFn(msg, queue)
        time_now = time_now + td_incr

if __name__ == "__main__":
    testQueue = sys.argv[1]
    spec_file = "specification.json"
    if len(sys.argv)>2:
        spec_file = sys.argv[2]
    queue = initQueue(testQueue)
    main(addMessageToQueue, queue, spec_file)
