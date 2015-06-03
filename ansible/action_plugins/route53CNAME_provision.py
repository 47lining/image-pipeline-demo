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
import json
import boto

from boto.route53.record import ResourceRecordSets

from ansible.runner.return_data import ReturnData
from ansible.utils import parse_kv, template
from ansible import utils

class ActionModule(object):
    def __init__(self, runner):
        self.runner = runner

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):

		try:

			args = {}
			if complex_args:
				args.update(complex_args)
			args.update(parse_kv(module_args))

			redshift_endpoint = args["redshift_endpoint"]
			cage = args["cage_name"]
			customer = args["customer_name"]

			envdict={}
			if self.runner.environment:
				env=template.template(self.runner.basedir, self.runner.environment, inject, convert_bare=True)
				env = utils.safe_eval(env)

			route53_conn = boto.connect_route53(aws_access_key_id=env.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key=env.get("AWS_SECRET_ACCESS_KEY"), security_token=env.get("AWS_SECURITY_TOKEN"))
			zones = route53_conn.get_hosted_zone_by_name("%s.%s.47lining.com" % (cage, customer))

			zone_id = zones["GetHostedZoneResponse"]["HostedZone"]["Id"]
			zone_id = zone_id[12:]

			recordset = ResourceRecordSets(route53_conn, zone_id)

			try:
				change = recordset.add_change("UPSERT", "redshift.%s.%s.47lining.com" % (cage, customer), "CNAME")
				change.add_value(redshift_endpoint)
				recordset.commit()
			except Exception, e:
				print "e: ", e
				change = recordset.add_change("CREATE", "redshift.%s.%s.47lining.com" % (cage, customer), "CNAME")
				change.add_value(redshift_endpoint)
				recordset.commit()
				
			return ReturnData(conn=conn,
                comm_ok=True,
                result=dict(failed=False, changed=False, msg="CNAME is created!"))

		except Exception, e:
			# deal with failure gracefully
			result = dict(failed=True, msg=type(e).__name__ + ": " + str(e))
			return ReturnData(conn=conn, comm_ok=False, result=result)
