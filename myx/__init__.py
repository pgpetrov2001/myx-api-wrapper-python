"""
Easy to use wrapper around the MYX's platform APIs.

Make a client that will authenticate you with the API with the supplied
credentials.
```
from myx import Client

client = Client("your.user@example.com", "your.password")
```

You can use this client to operate on your twins:

List all twins
--------------

```
for twin in client.get_twins():
   print(twin)
```


Make a new twin from drone images
---------------------------------
```
client.upload_images_from_fs("drone-flight-today/")
client.finish_upload("Made with the MYX Python library")
```

```
#imgs is an array of images which can be read like a binary file
client.upload_images(imgs, [f'image_{i}.jpg' for i, f in enumerate(imgs)])
#second argument you specify filenames for the images
```


Download a file from twin
-------------------------
```
ID = client.get_twins()[0].id
report = client.get_file(ID, "report.pdf")
if report is None:
    print("report.pdf not created yet. Try again later")
```
"""

from myx.client import Client
