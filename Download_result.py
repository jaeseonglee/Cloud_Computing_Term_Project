import boto3

s3 = boto3.resource('s3')

bucket = s3.Bucket(name = 'cc--result-js')

for b in bucket.objects.all():
    s3.meta.client.download_file('cc--result-js', b.key, b.key)



