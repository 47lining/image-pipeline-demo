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
from nucleator.cli.command import Command
from nucleator.cli.utils import ValidateCustomerAction

class BucketAndQ(Command):
    """
    A no-op command - provides access to ansible playbooks through utility functions,
    but does not interact with the nucleator cli parser.
    """

    name = "bucketandq"

    def provision(self, **kwargs):
        """
        Provisions an S3 bucket and an SQS queue within specified Account for specified Customer.
        """
        cli = Command.get_cli(kwargs)
        cage = kwargs.get("cage", None)
        customer = kwargs.get("customer", None)
        if cage is None or customer is None:
            raise ValueError("cage and customer must be specified")
        app_name = kwargs.get("app_name", "pipeline")
        redshift_db_name = kwargs.get("redshift_database_name", None)
        if redshift_db_name is None:
            redshift_db_name = "defaultdb"
        extra_vars={
            "cage_name": cage,
            "customer_name": customer,
            "app_name": app_name,
            "verbosity": kwargs.get("verbosity", None),
            "rs_username": kwargs.get("redshift_username", None),
            "rs_password": kwargs.get("redshift_password", None),
            "rs_dbname": redshift_db_name,
            "rs_url": kwargs.get("redshift_url", None),
        }
        
        command_list = []
        command_list.append("account")
        command_list.append("cage")  # because stackset/ansible/roles/instan... depends on cage_provision
        command_list.append("bucketandq")
        cli.obtain_credentials(commands = command_list, cage=cage, customer=customer, verbosity=kwargs.get("verbosity", None))
        
        return cli.safe_playbook(self.get_command_playbook("bucketandq-provision.yml"),
            is_static=True, # do not use dynamic inventory script, credentials may not be available
            **extra_vars
        )

    def parser_init(self, subparsers):
        """
        Initialize parsers for this command.
        """
        # add parser for cage command
        setup_parser = subparsers.add_parser(self.name)
        setup_subparsers=setup_parser.add_subparsers(dest="subcommand")
        beanstalk_provision=setup_subparsers.add_parser('provision', help="provision a new nucleator bucketandq stackset")
        beanstalk_provision.add_argument("--customer", required=True, action=ValidateCustomerAction, help="Name of customer from nucleator config")
        beanstalk_provision.add_argument("--cage", required=True, help="Name of cage from nucleator config")
        beanstalk_provision.add_argument("--app_name", required=True, help="Name of Application (will be used in bucket and queue names")
        beanstalk_provision.add_argument("--redshift_username", required=True, help="The username used to provision the redshift cluster")
        beanstalk_provision.add_argument("--redshift_password", required=True, help="The password used to provision the redshift cluster")
        beanstalk_provision.add_argument("--redshift_url", required=True, help="The stackset url of the redshift cluster")
        beanstalk_provision.add_argument("--redshift_database_name", required=False, help="The database name used to provision the redshift cluster")

# Create the singleton for auto-discovery
command = BucketAndQ()