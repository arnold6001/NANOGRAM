from storages.backends.s3boto3 import S3Boto3Storage

class CDNBucketStorage(S3Boto3Storage):
    default_acl = 'public-read'
    querystring_auth = True
    querystring_expire = 3600
    file_overwrite = False