# MediaConvert Configuration Sample
​
This document serves as a guide for configuring output groups in MediaConvert, outlining how the output of your media conversion is organized. Two methods, `set_video_transcode_output_location` and `set_audio_transcode_output_location` within `mediaconvert.py`, handle video and audio MediaConvert configurations.
​
## Video Configuration
​
### OutputGroups
​
OutputGroups in MediaConvert are configurations that specify how the output should be formatted and delivered. For details, check the [MediaConvert API Reference](https://docs.aws.amazon.com/pdfs/mediaconvert/latest/apireference/mediaconvert-api.pdf#page=302&zoom=100,160,542).
In our implementation, in the `set_video_transcode_output_location` function of `mediaconvert.py`, for each output group, their configuration (`OutputGroupSettings`) is modified based on the output group's name.
​
#### OutputGroupSettings
​
OutputGroupSettings in MediaConvert are similar to OutputGroupSettings in MediaLive, providing settings for organizing and delivering the output. For details, check the [MediaLive API Reference](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=193&zoom=100,96,244).
​
In our implementation, for instance, if the output group is named 'Apple HLS', the `HlsGroupSettings` inside `OutputGroupSettings` is adjusted, setting the `Destination` to an S3 bucket URL. If the `CustomName` is 'Thumbs', in addition to storing the transcoded video in S3, thumbnails are also saved in the `Destination` URL.
​
### Inputs
​
Inputs define the sources for your media conversion. 
In our implementation, the video path to transcode is set, updating the `FileInput` value inside the `Inputs`, incorporating a new .mp4 file into the variable.
For details, check the [MediaConvert API Reference](https://docs.aws.amazon.com/pdfs/mediaconvert/latest/apireference/mediaconvert-api.pdf#page=304&zoom=100,160,349).
​
## Audio Configuration
​
Similar modifications are made in the `set_audio_transcode_output_location` function. For each output group, if the output group is named 'File Group' the URL destination to S3 is added to the output group's settings and the audio path for transcoding is also stored in S3.