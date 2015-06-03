# Copyright 2015 47Lining LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import uuid, time, boto, json, sys
from boto.sqs.message import RawMessage
from datetime import datetime, date, time, timedelta
from os import path

from ansible.runner.return_data import ReturnData
from ansible.utils import parse_kv, template
from ansible import utils



class ActionModule(object):
    def __init__(self, runner):
        self.runner = runner

    # Connect to SQS and open the queue
    def initQueue(self, queue_name, region, env):
        # sqs = boto.connect_sqs()
        conn = boto.sqs.connect_to_region(region, aws_access_key_id=env.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key=env.get("AWS_SECRET_ACCESS_KEY"), security_token=env.get("AWS_SECURITY_TOKEN"))
        # queue = sqs.create_queue(queue_name)
        print "Attempting to connect to queue "+queue_name
        queue = conn.get_queue(queue_name)
        if queue is None:
            print "Connect failed."
            print conn.get_all_queues()
        print "Connected, creating sqs messages..."
        return queue

    # Pushes a message onto the queue
    def addMessageToQueue(self, message, queue):
        # Data required by the API
        data = {
            'key': str(uuid.uuid1()),
            'date': str(message)
        }

        # Put the message in the queue
        m = RawMessage()
        m.set_body(json.dumps(data))
        status = queue.write(m)

    def main(self, msgFn, queue, spec_file):
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

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):

        try:

            args = {}
            if complex_args:
                args.update(complex_args)
            args.update(parse_kv(module_args))

            envdict={}
            if self.runner.environment:
                env=template.template(self.runner.basedir, self.runner.environment, inject, convert_bare=True)
                env = utils.safe_eval(env)

            testQueue = args["queue_name"]
            region = args["region"]

            spec_file = path.expanduser("~/.nucleator/contrib/Bucketandq/orchestrator/specification.json")

            queue = self.initQueue(testQueue, region, env)
            self.main(self.addMessageToQueue, queue, spec_file)

            return ReturnData(conn=conn,
                comm_ok=True,
                result=dict(failed=False, changed=False, msg="Bucketandq Messages Created!"))

        except Exception, e:
            # deal with failure gracefully
            result = dict(failed=True, msg=type(e).__name__ + ": " + str(e))
            return ReturnData(conn=conn, comm_ok=False, result=result)
