from google.cloud import storage

def upload_to_gcp_bucket(source_file, bucket_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file)
    print(f"Uploaded {source_file} to GCP bucket {bucket_name}")