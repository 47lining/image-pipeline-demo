#!/bin/bash
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

echo "Enter the distributor beanstalk url: "
read queue_url
export queue_url

echo "Enter the 1 for first dataset and 2 for second: "
read dataset_number
export dataset_number

if [ "$dataset_number" = "1" ]
then
    message_text='{"redshift_initial_copy":"Running_intial_data_copy_command"}'
    export message_text
elif [ "$dataset_number" = "2" ]
then
    message_text='{"redshift_second_copy":"Running_second_data_copy_command"}'
    export message_text
else
	echo "Did not enter '1' or '2'. Message not sent to queue."
	exit 1
fi

aws sqs send-message --queue-url $queue_url --message-body $message_text