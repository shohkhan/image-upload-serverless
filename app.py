from os import environ as env

# 3rd party imports
from chalice import Chalice, Response
import boto3
from botocore.exceptions import ClientError
import uuid
import json

# TODO: add logging in the future
# import logging

app = Chalice(app_name='upload-image-serverless')


# Private methods
def __check(s3client, key, bucket_name):
    """
    This function checks whether a key exists in the bucket.
    Returns True if exists.
    """
    try:
        s3client.head_object(Bucket=bucket_name, Key=key)
    except ClientError as e:
        return int(e.response['Error']['Code']) != 404
    return True


def __check_metadata(s3client, key, bucket_name):
    """
    This function checks the metadata of the object to check whether the status is uploaded.
    Returns True of the status is uploaded, else returns False.
    """
    response = s3client.head_object(Bucket=bucket_name, Key=key)
    if 'status' in response['Metadata']:
        return response['Metadata']['status'] == 'uploaded'
    return False


def __initiate_s3client():
    """
    This sets the region and initiates the S3 client.
    """
    boto3.setup_default_session(region_name=env.get('region'))
    s3client = boto3.client(
        's3',
        aws_access_key_id=env.get('access_key_id'),
        aws_secret_access_key=env.get('secret_access_key')
    )
    return s3client


# API routes
@app.route('/image', methods=['POST'])
def upload_image():
    """
    Generates the pre-signed post URL
    """
    s3client = __initiate_s3client()
    # Generate random UUIDs as image ids
    image_id = str(uuid.uuid4())
    # Generate pre-signed POST url
    url_info = s3client.generate_presigned_post(
        Bucket=env.get('bucket'),
        Key=image_id
    )
    return Response(status_code=201,
                    headers={'Content-Type': 'application/json'},
                    body={'status': 'success',
                          'upload_url': url_info,
                          'id': image_id})


@app.route('/image/{image_id}', methods=['PUT'])
def update_image(image_id):
    """
    Updates the metadata of the image indicating the status is uploaded
    """
    # Parse body for status information
    request_body = app.current_request.json_body
    if request_body:
        request_body = json.loads(request_body)
        if 'status' in request_body and request_body['status'] == 'uploaded':
            s3client = __initiate_s3client()
            if __check(s3client, image_id, env.get('bucket')):
                # Update metadata if file exists
                s3client.copy_object(
                    CopySource={'Bucket': env.get('bucket'), 'Key': image_id},
                    Bucket=env.get('bucket'),
                    Key=image_id,
                    Metadata={'status': 'uploaded'},
                    MetadataDirective='REPLACE'
                )
                return Response(status_code=200,
                                headers={'Content-Type': 'application/json'},
                                body={'status': 'success'})
    return Response(status_code=400,
                    headers={'Content-Type': 'application/json'},
                    body={'status': 'failed'})


@app.route('/image/{image_id}', methods=['GET'])
def download_image(image_id):
    """
    This returns the pre-signed download
    """
    s3client = __initiate_s3client()
    if __check(s3client, image_id, env.get('bucket')) and __check_metadata(s3client, image_id, env.get('bucket')):
        # Parse the query parameters for timeout
        query_params = app.current_request.query_params
        if query_params and 'timeout' in query_params:
            timeout = int(query_params['timeout'])
        else:
            timeout = int(env.get('default_timeout'))
        # Generate the pre-signed URL
        url = s3client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': env.get('bucket'),
                'Key': image_id
            },
            ExpiresIn=timeout
        )
        return Response(status_code=200,
                        headers={'Content-Type': 'application/json'},
                        body={
                            "status": "success",
                            "download_url": url
                        })
    return Response(status_code=400,
                    headers={'Content-Type': 'application/json'},
                    body={"status": "failed"})
