#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2017 Strikingly.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""" Cloudwatch class for logging """

from __future__ import absolute_import, division, print_function, unicode_literals

import boto3
from botocore.exceptions import ClientError

# From http://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutLogEvents.html
# maximum size in bytes of Log Events (with overhead) per invocation of PutLogEvents
MAX_BATCH_SIZE = 1048576
MAX_BATCH_COUNT = 10000  # maximum number of Log Events per invocation of PutLogEvents
LOG_EVENT_OVERHEAD = 26  # bytes of overhead per Log Event

CF_LOG = boto3.client("logs")


class Cloudwatch(object):

    """
    Cloudwatch class help divided a list of logs into chunk and send.

    :type log_group_name: string
    :param log_group_name: AWS Cloudwatch log group name
    :type log_stream_name: string
    :param log_stream_name: AWS Cloudwatch log stream name

    """

    def __init__(self, log_group_name, log_stream_name):
        self._log_group = log_group_name
        self._log_stream = log_stream_name

    @property
    def log_group_name(self):
        """ Read only log group name """
        return self._log_group

    @property
    def log_stream_name(self):
        """ Read only log stream name """
        return self._log_stream

    def _put_log_events(self, sequence_token, batches):
        ''' Recurisive function to send log batch '''
        if len(batches) < 1:
            return

        kwargs = dict(logGroupName=self.log_group_name, logStreamName=self.log_stream_name,
                      logEvents=batches.pop(0))
        if sequence_token is not None:
            kwargs["sequenceToken"] = sequence_token
        response = None

        for _ in range(3):
            try:
                response = CF_LOG.put_log_events(**kwargs)
                break
            except ClientError as err:
                if err.response.get("Error", {}).get("Code") in ("DataAlreadyAcceptedException",
                                                                 "InvalidSequenceTokenException"):
                    kwargs["sequenceToken"] = err.response["Error"]["Message"].rsplit(
                        " ", 1)[-1]
                else:
                    raise
        if response is None or "rejectedLogEventsInfo" in response:
            raise Exception("Failed to deliver logs: {}".format(response))
        self._put_log_events(response["nextSequenceToken"], batches)


    def send_logs(self, logs):
        ''' Divide logs into batch and send '''
        def _size(_log):
            return (len(_log["message"]) if isinstance(_log, dict) else 1) + LOG_EVENT_OVERHEAD

        def _truncate(_msg):
            print("Log message size exceeds max payload size, truncated")
            return _msg[:MAX_BATCH_SIZE - LOG_EVENT_OVERHEAD]

        # Devide batches based on aws api limits
        batches = []
        batch = []
        batch_size = 0
        for log in logs:
            if _size(log) > MAX_BATCH_SIZE:
                log['message'] = _truncate(log['message'])
            if batch_size + _size(log) > MAX_BATCH_SIZE or len(batch) == MAX_BATCH_COUNT:
                batches.append(batch)
                batch = []
                batch_size = 0
            batch.append(log)
            batch_size = batch_size + _size(log)
        batches.append(batch)
        self._put_log_events(None, batches)
