import os
import requests
import json
import mimetypes
from collections.abc import Iterable

_BASE_URL_PROD = 'https://myxrobotics.com'
_BASE_URL_TEST = 'http://localhost:4213'
_BASE_URL = _BASE_URL_PROD

"""
class Twin:
    def __init__(self, id: str, name: str, latitude, longitude, capture_date):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.capture_date = capture_date

    def __str__(self):
        return f'Twin(id={self.id} name={self.name})'
"""

def _get_mime_from_fname(fname):
    ext, encoding = mimetypes.guess_type(fname)
    return ext


class Client():
    """All client functions return the response in json format, except for get_file"""

    def __init__(self, email: str, password: str, base_url=_BASE_URL):
        self.base_url = base_url
        self.session = self._get_session({'email': email, 'password': password})


    def _get_session(self, creds):
        sess = requests.Session()
        r = sess.post(f'{self.base_url}/users/login/', data=creds, allow_redirects=False)

        if r.headers['location'] != '/dashboard/':
            raise Exception("Failed to authenticate. Check your email and password are correct.")

        return sess


    def _get_resource(self, route: str, trail=True, **kwargs):
        url = f'{self.base_url}/{route}{"/" if trail else ""}'
        res = self.session.get(url, **kwargs)
        return self._give_response(res, url)


    def _post_resource(self, route: str, trail=True, **kwargs):
        url = f'{self.base_url}/{route}{"/" if trail else ""}'
        res = self.session.post(url, **kwargs)
        return self._give_response(res, url)


    def _give_response(self, res, url: str):
        """A wrapper for throwing exceptions depending on http response"""
        if res.status_code == 403:
            raise PermissionError(f'At url "{url}": Permission denied')

        if res.status_code == 404:
            raise Exception(f'Requested url "{url}" was not found')

        if res.status_code == 200:
            return res

        raise Exception(f"At url {url}: Unexpected status code {res.status_code}")

    def get_file(self, twin_id: int, file_path: str):
        f""" Download a file if it exists. Returns a file-like object from which you can read in binary mode.
        Some twin files are generated by MYX."""
        return self._get_resource(f'twins/{twin_id}/data/{file_path}', trail=False, stream=True).raw


    def upload_images_from_fs(self, target):
        """A convenient wrapper for the method upload_images, accepts a directory or 
        an iterable of filenames."""
        fnames = target

        #if target is a string then target is a path to a directory
        if type(target) is str:
            if os.path.isdir(target):
                fnames = map(lambda fname: os.path.join(target, fname), os.listdir(target))
            else:
                raise Exception('Specified target is not a directory')

        elif not isinstance(target, Iterable):
            raise TypeError(f'{type(target)} is not a valid type for argument target.')

        return self.upload_images(map(
            lambda fname: open(fname, mode='rb'), 
            fnames
        ), fnames)


    def upload_images(self, images, fnames):
        """Pass an iterable of file-like objects opened in binary mode
        and an iterable with their respective filenames"""
        ret = []

        for img, fname in zip(images, fnames):
            #print('sending file', (fname, img, _get_mime_from_fname(fname)))
            ret.append(self._post_resource('upload', files={
                'file': (fname, img, _get_mime_from_fname(fname))
            }).json())

        return ret


    def _checkout(self):
        """Checkout only if you have enough balance.
        Returns a skip code to be passed as a payment intent id."""
        return self._post_resource('payment/checkout').json()['skipCode']

    def finish_upload(self, twin_name=''):
        """ Give a name for the new twin and notify MYX that there will be no more images uploaded. This
        triggers the processing pipeline to start working on your data """
        #post /payment/checkout/ to start returns client secret
        #stripe request with clientSecret:paymentIntentId and card html element need stripe library
        #post /upload/finish/:paymentIntentId:/ with {name:twinName}
        paymentIntentId = self._checkout()
        return self._post_resource(f'upload/finish/{paymentIntentId}', data={'name': twin_name})

    def get_annotations(self, twin_id: int):
        """ Get a list of all annotations for a given twin. """
        return self._get_resource(f'twins/{twin_id}/annotations').json()

    def make_new_annotation(self, twin_id: int, position_x: float, position_y: float, position_z: float, label: str, iframeURL: str, notes: str):
        """ Make a new annotation at the given position, with the given label, url and additional notes. """
        return self._post_resource(f'twins/{twin_id}/annotations', json = {
            'x': position_x,
            'y': position_y,
            'z': position_z, 
            'label': label,
            'iframeURL': iframeURL,
            'notes': notes,
            'TwinId': twin_id
        }).json()


    #keep it prefixed with underscore until api-docs is merged with master
    def _get_twins(self) :
        """ Get a list of all twins you own. """
        return self._get_resource('api/list_all').json()
        #Twin(str(json['id']), json['name'], json['latitude'], json['longitude'], json['captureDate'])

    #keep it prefixed with underscore until api-docs is merged with master
    def _make_new_twin(self, name=None): # was a name required when submitting it from a form?
        """ Make a new twin. """
        return _post_resource('api/make_twin', json={"name": name}).json()
        #return Twin(str(json['id']), json['name'], None, None, None)

