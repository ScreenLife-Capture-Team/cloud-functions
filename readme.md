# ScreenLife Capture Cloud Functions

This repo contains the cloud functions used during the ScreenLife Capture study.

## Functions

**register** 

```
POST {
	"username": string,
	"key": string
}
Responses
- 201 Created
- 405 Invalid method (only POST)
- 409 User already exists
```

**upload_file** 

```
POST {
	"username": string,
	"key": string
}
(include images to upload under `files`)
Responses
- 201 Successfully Uploaded
- 404 Invalid username/key
- 405 Invalid method (only POST)
```

**count_files**

```
POST {
	"username": string,
	"key": string,
	"fileNames": string[]
}
Responses
- 200 All files verified
- 400 Files missed, list of missed files under `missedPictures`
- 404 Invalid username/key
- 405 Invalid method (only POST)
```

