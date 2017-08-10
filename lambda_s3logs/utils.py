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

""" Utilities """

from __future__ import absolute_import, division, print_function, unicode_literals

import csv
import gzip
import json
import re
import email
from datetime import datetime
import boto3

S3 = boto3.client('s3')
S3R = boto3.resource('s3')


def unpack_data_from_s3(event):
    ''' load object from s3 CreateObject event '''
    # split bucket and filepath to variables
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print("Processing file s3://{}/{}".format(bucket, key))
    response = S3.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    # If the name has a .gz extension, then decompress the data
    if key[-3:] == '.gz':
        data = gzip.decompress(data)
    return data


def parse_data(data, log_format):
    ''' parse data into json format logs '''
    logs = []
    # when there is specitial charater that not belong to utf-8, escape it
    data = str(data, 'utf-8', errors='backslashreplace').splitlines()
    result = csv.DictReader((row for row in data if not row.startswith('#')),
                            fieldnames=log_format, delimiter='\t')
    for row in result:
        date = row.pop('logdate')
        time = row.pop('logtime')
        log = {
            'message': json.dumps(row),
            'timestamp': int(datetime.strptime(
                date + " " + time, '%Y-%m-%d %H:%M:%S').timestamp() * 1000)
        }
        logs.append(log)
    logs.sort(key=lambda x: x['timestamp'])
    return logs


def extract_email_and_upload(data, bucket, prefix):
    """ Extract akamai LDS email data in gzip/mime type """
    try:
        # Read the bytes into a Email Object
        msg = email.message_from_bytes(data)
        filename = msg['subject']
        if not filename or not filename.endswith('.gzm'):
            print("Invalid file, subject is: " + filename)
            return 1
        regx = re.compile('.gzm\\b')
        count = 0
        for part in msg.walk():
            decoded_filename = regx.sub(str(count) + '.gz', filename)
            # multipart/* are just containers
            if part.get_content_maintype() == 'multipart':
                continue
            upload_objects_to_s3(
                bucket, prefix + decoded_filename, part.get_payload(decode=True))
            count += 1
        return 0
    except Exception as err:
        raise err


def upload_objects_to_s3(bucket, key, data):
    ''' Upload data to s3 '''
    S3R.Object(bucket, key).put(Body=data)
