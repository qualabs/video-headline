import React, {Component} from 'react'

import ReactS3Uploader from 'react-s3-uploader-qualabs'

import {FETCH_VIDEO} from '../../../actions/video'

import './index.css'

export default class AudioUploaderDropzone extends Component {
  constructor (props) {
    super(props)
    this.getSignedUrl = this.getSignedUrl.bind(this)
    this.onProgress = this.onProgress.bind(this)
    this.onUploadError = this.onUploadError.bind(this)
    this.onUploadFinish = this.onUploadFinish.bind(this)
  }

  getType = (file) => {
    const {isAudio} = this.props
    let fileType = file.type

    if (isAudio) {
      fileType = `audio/mp4`
    }

    return fileType
  }


  getSignedUrl (file, callback) {
    let content_type = file.type
    let media_type = 'video'

    if (this.props.isAudio) {
      content_type = 'audio/mp4'
      media_type = 'audio'
    }

    const params = {
      name: file.name,
      content_type: content_type,
      action: FETCH_VIDEO,
      media_type: media_type,
    }
    this.props.createVideo(params).then( data => {
      callback({signedUrl: data.data.signed_url})
    })
  }

  onProgress (percent) {
    this.props.updateProgress(percent)
  }

  onUploadError () {
    this.props.deleteVideo()
  }

  onUploadFinish () {
    this.props.uploadFinished()
  }

  render () {
    let accept = 'video/*'
    let filename = 'input.mp4'
    let dropZoneText = 'video'

    if (this.props.isAudio) {
      accept = 'audio/*'
      filename = 'output.mp4'
      dropZoneText = 'audio'
    }

    return (
      <div className='dropzone container-fluid text-center'>
        <div className='dropzone-icon'>
          <i className='fas fa-cloud-upload-alt fa-9x' />
          <p>{`Click here or drop a file of ${dropZoneText}`}</p>
        </div>
        <ReactS3Uploader
          className='dropzone-input'
          preprocess={this.preprocess}
          getSignedUrl={this.getSignedUrl}
          accept={accept}
          onSignedUrl={this.onSignedUrl}
          onProgress={this.onProgress}
          onError={this.onUploadError}
          onFinish={this.onUploadFinish}
          autoUpload={true}
          uploadRequestHeaders={{'x-amz-acl': 'private'}}
          scrubFilename={() => filename}
          uploadFileType={'audio/mp4'}
          getType={this.getType}
        />
      </div>
    )
  }
}
