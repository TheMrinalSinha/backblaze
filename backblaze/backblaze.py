from requests import get
from base64   import b64encode

from .utils   import _get_output

class Backblaze(object):
    def __init__(self, account_id, application_id):
        self.application_id = application_id
        self.account_id     = account_id
        self.id_and_key     = '{}:{}'.format(self.account_id, self.application_id)
        self.auth_string    = 'Basic ' + b64encode(self.id_and_key.encode()).decode()
        self.headers        = {'Authorization' : self.auth_string}

        self.api_url        = None
        self.auth_token     = None
        self.upload_url     = None
        self.download_url   = None

    def validate(self):
        request = get('https://api.backblazeb2.com/b2api/v1/b2_authorize_account',
                  headers = self.headers)
        if request.ok:
            response          = request.json()
            self.api_url      = response.get('apiUrl')
            self.auth_token   = response.get('authorizationToken')
            self.download_url = response.get('downloadUrl')
            return True
        return False

    def buckets(self, bucket_name=None):
        if self.validate():
            request = get('%s/b2api/v1/b2_list_buckets' % self.api_url,
                params  = {'accountId' : self.account_id},
                headers = {'Authorization' : self.auth_token})
            if request.ok:
                if bucket_name:
                    return [bkt['bucketId'] for bkt in request.json()
                           ['buckets'] if bkt['bucketName'] == bucket_name][0]
                return request.json()
            return False

    def _upload_url(bucket_name):
        bucket_id = self.buckets(bucket_name)
        request   = get('%s/b2api/v1/b2_get_upload_url' % self.api_url,
                    params  = {'bucketId' : bucket_id},
                    headers = {'Authorization' : self.auth_token})
        return request.json()['uploadUrl']

    def upload(self, bucket_name, upload_file):
        self.upload_url = _upload_url(bucket_name)