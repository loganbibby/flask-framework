import tempfile
import boto3
import botocore
from StringIO import StringIO
from flask import current_app

class S3Error(Exception): pass

def get_s3_object(bucket, key):
    s3 = boto3.resource('s3')
    return s3.Object( bucket, key )

def process_response(response):
    statuscode = response['ResponseMetadata']['HTTPStatusCode']
    requestid = response['ResponseMetadata']['RequestId']

    if statuscode in [200, 201, 204]:
        return requestid
    else:
        current_app.logger.debug('S3 error for request %s: %s' % (requestid, response))
        raise S3Error('Request ID: %s - Error Code: %s - See log for full response.' % (requestid, statuscode))

def upload_file(bucket, key, fh, mimetype, acl='private'):
    current_app.logger.debug('Uploading %s file to S3 %s/%s as %s' % (mimetype, bucket, key, acl))

    response = get_s3_object(bucket, key).put(
        ACL=acl,
        Body=fh.read(),
        ContentType=mimetype
    )

    requestid = process_response(response)
    current_app.logger.info('S3 response to file upload was OK to request %s' % requestid)
    return requestid

def download_file(bucket, key):
    current_app.logger.debug('Downloading S3 file from %s/%s' % (bucket, key))

    response = get_s3_object(bucket, key).get()

    requestid = process_response(response)
    current_app.logger.info('S3 response to file download was OK to request %s' % requestid)

    return StringIO( response['Body'].read() )

def delete_file(bucket, key):
    current_app.logger.debug('Deleting S3 file from %s/%s' % (bucket, key))

    response = get_s3_object(bucket, key).delete()

    requestid = process_response(response)
    current_app.logger.info('S3 response to file deletion was OK to request %s' % requestid)
    return requestid
