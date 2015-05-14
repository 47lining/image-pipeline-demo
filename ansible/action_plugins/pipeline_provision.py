import json
import boto
import yaml
import os
import time

from boto.datapipeline import layer1
from boto import datapipeline
from boto.regioninfo import RegionInfo

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

			app_name = args["app_name"]
			account_name = args["account_name"]
			pipeline_resource_role = args["pipeline_resource_role"]
			region = args["region"]
			pipeline_template = args["pipeline_template"]

			pipeline_name = "%s-%s-DataPipeline" % (app_name, account_name)
			unique_id = "%s-%s-DataPipeline-UniqueID" % (app_name, account_name)

			envdict={}
			if self.runner.environment:
				env=template.template(self.runner.basedir, self.runner.environment, inject, convert_bare=True)
				env = utils.safe_eval(env)

			stream = open(pipeline_template)
			pipelinedefinition = json.load(stream)

			c = boto.connect_iam(aws_access_key_id=env.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key=env.get("AWS_SECRET_ACCESS_KEY"), security_token=env.get("AWS_SECURITY_TOKEN"))
			
			try:
				c.get_instance_profile(pipeline_resource_role)
				c.remove_role_from_instance_profile(pipeline_resource_role, pipeline_resource_role)
				c.delete_instance_profile(pipeline_resource_role)
				c.create_instance_profile(pipeline_resource_role)
				c.add_role_to_instance_profile(pipeline_resource_role,pipeline_resource_role)
			except Exception, e:
				c.create_instance_profile(pipeline_resource_role)
				c.add_role_to_instance_profile(pipeline_resource_role,pipeline_resource_role)

			connection = datapipeline.connect_to_region(region, aws_access_key_id=env.get("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=env.get("AWS_SECRET_ACCESS_KEY"),
                    security_token=env.get("AWS_SECURITY_TOKEN"))

			connection.auth_service_name = 'datapipeline'

			response = connection.create_pipeline(pipeline_name, unique_id)

			pipeline_id = response['pipelineId']

			connection.put_pipeline_definition(pipelinedefinition, pipeline_id)

			connection.activate_pipeline(pipeline_id)

			return ReturnData(conn=conn,
                comm_ok=True,
                result=dict(failed=False, changed=False, msg="Pipeline is created!"))

		except Exception, e:
			# deal with failure gracefully
			result = dict(failed=True, msg=type(e).__name__ + ": " + str(e))
			return ReturnData(conn=conn, comm_ok=False, result=result)

