#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Basic interface to the Amazon S3 database."""

import os
import uuid
import boto3
import botocore
import logging

logger = logging.getLogger(__name__)


class AmazonS3:
    """Basic interface to the Amazon S3 database."""

    _DEFAULT_REGION_NAME = 'us-east-1'
    _DEFAULT_BUCKET_NAME = 'boosters-manifest'
    _DEFAULT_LOCAL_ENDPOINT = 'http://127.0.0.1:9000'  # MINIO server
    _DEFAULT_ENCRYPTION = 'aws:kms'
    _DEFAULT_VERSIONED = True

    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, bucket_name=None,
                 region_name=None, endpoint_url=None, use_ssl=False, encryption=None,
                 versioned=None, local_dev=False):
        """Initialize object, setup connection to the AWS S3."""
        self._s3 = None

        self.region_name = os.getenv(
            'AWS_S3_REGION') or region_name or self._DEFAULT_REGION_NAME
        self.bucket_name = bucket_name or self._DEFAULT_BUCKET_NAME
        self._aws_access_key_id = os.getenv(
            'AWS_S3_ACCESS_KEY_ID') or aws_access_key_id
        self._aws_secret_access_key = \
            os.getenv('AWS_S3_SECRET_ACCESS_KEY') or aws_secret_access_key

        self._local_dev = local_dev
        # let boto3 decide if we don't have local development proper values
        self._endpoint_url = self._DEFAULT_LOCAL_ENDPOINT
        self._use_ssl = True
        # 'encryption' (argument) might be False - means don't encrypt
        self.encryption = self._DEFAULT_ENCRYPTION if encryption is None else encryption
        self.versioned = self._DEFAULT_VERSIONED if versioned is None else versioned

        # if we run locally, make connection properties configurable
        if self._local_dev:
            logger.info("Running S3 locally on: {}".format(self._endpoint_url))
            self._use_ssl = use_ssl
            self.encryption = False

        if self._aws_access_key_id is None or self._aws_secret_access_key is None:
            logger.critical("AWS configuration not provided correctly, "
                            "both key id and key is needed")

    def object_exists(self, object_key):
        """Check if the there is an object with the given key in bucket, does only HEAD request."""
        try:
            self._s3.Object(self.bucket_name, object_key).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                exists = False
            else:
                raise
        else:
            exists = True
        return exists

    def connect(self):
        """Connect to the S3 database."""
        try:
            session = boto3.session.Session(aws_access_key_id=self._aws_access_key_id,
                                            aws_secret_access_key=self._aws_secret_access_key,
                                            region_name=self.region_name)
            # signature version is needed to connect to new regions which support only v4
            if self._local_dev:
                self._s3 = session.resource('s3', config=botocore.client.Config(
                    signature_version='s3v4'),
                    use_ssl=self._use_ssl, endpoint_url=self._endpoint_url)
            else:
                self._s3 = session.resource('s3', config=botocore.client.Config(
                    signature_version='s3v4'), use_ssl=self._use_ssl)
            logger.info("Conneting to the s3")
        except Exception as exc:
            logger.info(
                "An Exception occurred while establishing a AmazonS3 connection {}"
                .format(str(exc)))

    def is_connected(self):
        """Check if the connection to database has been established."""
        return self._s3 is not None

    def disconnect(self):
        """Close the connection to S3 database."""
        del self._s3
        logger.info("Disconnected AmazonS3!")
        self._s3 = None

    @staticmethod
    def _get_fake_version_id():
        """Generate fake S3 object version id."""
        return uuid.uuid4().hex + '-unknown'

    def store_file(self, file_path, object_key):
        """Store file onto S3."""
        f = None
        try:
            f = open(file_path, 'rb')
            logger.info("opened file {}".format(file_path))
            return self.store_blob(f, object_key)
        finally:
            if f is not None:
                logger.info("closed file {}".format(file_path))
                f.close()

    def store_blob(self, blob, object_key):
        """Store blob onto S3."""
        put_kwargs = {'Body': blob}
        if self.encryption:
            put_kwargs['ServerSideEncryption'] = self.encryption

        response = self._s3.Object(
            self.bucket_name, object_key).put(**put_kwargs)

        if 'VersionId' not in response and self._local_dev and self.versioned:
            # If we run local deployment, our local S3 alternative does not
            # support versioning. Return a fake one.
            return self._get_fake_version_id()

        return response.get('VersionId')

    def retrieve_file(self, object_key, file_path):
        """Download an S3 object to a file."""
        try:
            self._s3.Object(self.bucket_name,
                            object_key).download_file(file_path)
        except Exception as exc:
            logger.error(
                "An Exception occurred while retrieving file \n".format(str(exc)))

    def retrieve_blob(self, object_key):
        """Retrieve remote object content."""
        try:
            return self._s3.Object(self.bucket_name, object_key).get()['Body'].read()
        except Exception as exc:
            logger.error(
                "An Exception occurred while retrieving blob\n {}".format(str(exc)))

    def list_bucket_objects(self):
        """List all the objects in bucket."""
        try:
            return self._s3.Bucket(self.bucket_name).objects.all()
        except Exception as exc:
            logger.error(
                "An Exception occurred while listing objects in bucket\n {}".format(str(exc)))

    def list_bucket_keys(self):
        """List all the keys in bucket."""
        try:
            return [i.key for i in self.list_bucket_objects()]
        except Exception as exc:
            logger.error(
                "An Exception occurred while listing bucket keys\n {}".format(str(exc)))

    def s3_delete_object(self, object_key):
        """Delete a object in bucket."""
        try:
            response = self._s3.Bucket(self.bucket_name).delete_objects(
                Delete={"Objects": [{'Key': object_key}]}
            )
            if 'VersionId' not in response and self._local_dev and self.versioned:
                # If we run local deployment, our local S3 alternative does not
                # support versioning. Return a fake one.
                return self._get_fake_version_id()
            return response.get('VersionId')
        except Exception as exc:
            logger.error(
                "An Exception occurred while deleting object\n {}".format(str(exc)))

    def s3_delete_objects(self, object_keys):
        """Delete a object in bucket."""
        try:
            if not isinstance(object_keys, list):
                raise ValueError("Expected {}, got {}".format(
                    type(list()), type(object_keys)))
            response = self._s3.Bucket(self.bucket_name).delete_objects(
                Delete={"Objects": [{'Key': k} for k in object_keys]}
            )
            if 'VersionId' not in response and self._local_dev and self.versioned:
                # If we run local deployment, our local S3 alternative does not
                # support versioning. Return a fake one.
                return self._get_fake_version_id()
            return response.get('VersionId')
        except Exception as exc:
            logger.error(
                "An Exception occurred while deleting objects \n {}".format(str(exc)))

    def s3_clean_bucket(self):
        """Clean the bucket."""
        try:
            all_keys = self.list_bucket_keys()
            self.s3_delete_objects(all_keys)
            logger.info(
                "`{}` bucket has been cleaned.".format(self.bucket_name))
        except Exception as exc:
            logger.error(
                "An Exception occurred while cleaning the bucket\n {}".format(str(exc)))
