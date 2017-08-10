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

""" Module root """

__version__ = '1.0.0'

from . import utils
from .cloudwatch import Cloudwatch

def handle_s3_logs(event, log_group, log_stream, log_format):
    """ The handler for s3 CreateObject event and send the logs to Cloudwatch

        :param event: AWS S3 ObjectCreate event
        :param log_group: AWS Cloudwatch log group name
        :param log_stream: AWS Cloudwatch log stream name
        :param log_format: A list of log fields
    """
    data = utils.parse_data(utils.unpack_data_from_s3(event), log_format)
    cloud_watch = Cloudwatch(log_group, log_stream)
    cloud_watch.send_logs(data)

def handle_s3_akamai_email(event, bucket, prefix=''):
    """ The handler for s3 CreateObject event to extract akamai log file from email and upload

        :param event: AWS S3 ObjectCreate event
        :param bucket: Output aws s3 bucket name
        :param prefix: Output aws s3 object key prefix
    """
    data = utils.unpack_data_from_s3(event)
    utils.extract_email_and_upload(data, bucket, prefix)
