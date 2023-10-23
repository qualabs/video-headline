# MediaLive Input Attachments Sample

This document guides you through the configuration of input attachments in MediaLive, specifically focusing on the `InputAttachment`.

## InputAttachment

An `InputAttachment` in MediaLive represents the connection of an input source to a channel. The key attribute is `InputId`, which refers to the ID of the input source.

This value is set dynamically every time a channel is created and has the only purpose of identifying the different inputs. (see create_channel method in medialive.py).
For details, check the [MediaLive API Reference](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=156).

# MediaLive Encoder Settings Samples

This section explores two samples related to encoder settings: `media_live_encoder_settings_economic.sample` and `media_live_encoder_settings.sample`.
While both serve the same purpose, the 'economic' variant provides a more concise configuration.

## EncoderSettings

`EncoderSettings` contains configurations for encoding settings in MediaLive, which are the configuration parameters and options utilized to manage the process of encoding audio and video content.

### TimecodeConfig

`TimecodeConfig` identifies the source for the timecode that will be associated with the events outputs, it is used for synchronizing and identifying frames within a video stream. There are three possible values: `EMBEDDED`, `SYSTEMCLOCK`, `ZEROBASED`. In our sample files we are using the `SYSTEMCLOCK` source.
For details, check the [MediaLive API Reference](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=206&zoom=100,96,174).

### OutputGroups

Output groups define how streams should be **distributed** for a Live Event. An output group is a collection of outputs within a MediaLive channel, an output is a collection of encodes.

#### OutputGroupSettings

Here is where you set up the configurations for each type of output group that you can use. Eg: HlsGroupSettings, RtmpGroupSettings, MsSmoothGroupSettings, ArchiveGroupSettings, etc.

For details and specifics of each configuration check the [MediaLive API Reference](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=193&zoom=100,96,244).

We also set one of the properties of this item in the create_channel method(medialive.py), we changed the DestinationRefId value using the organization S3 bucket name.

#### Outputs

`Outputs` within an output group define the specific output settings. There can be multiple outputs within a group, each specifying its own unique settings. `Outputs` is a list of output type-specific settings which describes how they should work.
It contains an array of outputs that describes each of them with specific settings.
For details, check the [MediaLive API Reference](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=190&zoom=100,96,813).

#### Name

The `Name` attribute represents a customizable identifier for an output group, offering users the option to define a unique name. In our context, the assigned name is "S3," reflecting the storage location for the associated values.

### GlobalConfiguration

`GlobalConfiguration` encompasses settings that apply to the event as a whole. For example the `SupportLowFramerateInputs` which supports streams with low frames per second.
For more details, check the [MediaLive API Reference](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=117&zoom=100,96,694).

### CaptionDescriptions

Settings for caption descriptions. For details, check the [CaptionDescriptions](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=84&zoom=100,96,796).

### VideoDescriptions

`VideoDescriptions` encapsulates video settings for each stream, providing a versatile list of configurations.

This allows multiple stream profiles, each with a specific codec settings. For example, you may have configurations for 1080p and 720p to accommodate diverse network conditions.

It's important to state that the **name** property will be used by outputs to uniquely identify their **VideoDescription**.

For example: in media_live_encoder_settings the output "video_1080p30" will use the videoDescription named "video_1080p30".


Check [VideoDescriptions](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=209&zoom=100,96,800) and [CodecSettings](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=209&zoom=100,96,404) for more details.

### AudioDescriptions

`AudioDescriptions` encapsulate audio settings within a stream. This includes `CodecSettings` for audio codec settings. Check [AudioDescriptions](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=70&zoom=100,96,840) and [CodecSettings](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=70&zoom=100,96,272) for more information.

# MediaLive Destination Sample

In this section, we'll delve into the `media_live_destination.sample` configuration.

## OutputDestination

`OutputDestination` represents the destination for your live stream. For detailed settings, refer to [OutputDestination](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=191&zoom=100,96,610).

### Id

User-specified ID. This is used in an output or output group. In our case, it is used in the `create_channel` method inside `medialive.py` and its value is the organization bucket name.

### OutputDestinationSettings

`OutputDestinationSettings` specify several configuration params.
In the create_channel method inside medialive.py, we set the URL specifying the destination where the output will be stored, in this case a AWS S3 bucket URL.
For details, check the [OutputDestinationSettings](https://docs.aws.amazon.com/pdfs/medialive/latest/apireference/medialive-api.pdf#page=192&zoom=100,96,213).