# Image Uploader Service - AWS Serverless #
### Sample AWS serverless program to upload and download images using presigned urls ###

#### What is this repository for? ####
This implements the uploader service on AWS serverless

#### How to get set up ####
It is highly recommended to use a new environment. I used conda to create a new environment:

    conda create -n [name_of_the_environment] python=3.6
    source activate [name_of_the_environment]

Several python libraries are used; notably:

- For creating and deploying application on AWS lambda, "chalice" is used.
- For AWS client and resource management "boto3" is used.
- For the demo: "requests" is used for creation of the POST, PUT and GET calls; "pillow" and "matplotlib" is used for visualization purposes.

Use pip to install all the requirement from the requirements.txt.

    pip install -r requirements.txt

Also the information on the following config file requires to be updated:

    image-uploader-serverless/.chalice/config.json

#### How to start the service ####
The service can be started locally using the following command at the "image-uploader-serverless" directory:

    chalice local

The service can be deployed using the following command:

    chalice deploy

#### Assumptions ####
Few assumptions are made to make the task simple:
- Only the 'status' information on the image metadata uploaded to the S3 is relevant.
