from google.cloud import storage
from werkzeug.utils import secure_filename
import os
import asyncio

PROJECT_ID = ""
BUCKET_NAME = ""

NUM_FILES = 1000
client = storage.Client(project=PROJECT_ID)
bucket = client.get_bucket(BUCKET_NAME)


def gbucket_upload(file_object, destination_blob_name, bucket):
    """Uploads a file to the bucket."""
    destination_blob_name = list(destination_blob_name)
    destination_blob_name[8] = "/"
    destination_blob_name = "".join(destination_blob_name)
    blob = bucket.blob(destination_blob_name)
    public_url = blob.upload_from_file(file_object)
    return public_url


async def upload_file_to_bucket(file, filename, bucket):
    """Wrapper for running program in an asynchronous manner"""
    loop = asyncio.get_event_loop()
    # save the file locally in the /tmp/filename
    file.save("/tmp/" + filename)
    try:
        # take the file from the local folder then upload it
        await loop.run_in_executor(None, gbucket_upload, open("/tmp/" + filename, 'rb'), filename, bucket)
    except Exception as e:
        print(f"Exception occured: {e}")


async def upload_files_to_bucket(files, filenames):
    await asyncio.gather(*[upload_file_to_bucket(file, filename, bucket) for file, filename in
                        zip(files, filenames)])

def count_files_with_name(user):
    name = list(user)
    name[8] = "/"
    name = "".join(name)
    return len(list(client.list_blobs(bucket, prefix=name)))


async def count_files_with_names(users):
    loop = asyncio.get_event_loop()
    return await asyncio.gather(*[loop.run_in_executor(None, count_files_with_name, user) for user in users])

def count_files(filenames):
    counts = asyncio.run(count_files_with_names(filenames))
    missed = []

    for fname, count in zip(filenames, counts):
        if count == 0:
            missed.append(fname)
    
    if not missed:
        return True
    return False


def upload(request):
    if request.method == 'POST':

        # Retrieve files
        files = []
        for i in range(1, NUM_FILES + 1):
            file = request.files.get(f'file{i}', None)
            if not file: break
            files.append(file)

        # Extract filenames and filepaths to save to
        filenames = [secure_filename(file.filename) for file in files]

        # Try uploading the files to the bucket
        try:
            asyncio.run(upload_files_to_bucket(files, filenames))
            if count_files(filenames):
                return dict(msg=f'{len(filenames)} files uploaded'), 201
            else:
                return dict(msg="Count failed"), 500

        except Exception as e:
            print(e)
            return dict(msg=str(e)), 400

    else:
        return dict(msg="Only Post method allowed"), 405