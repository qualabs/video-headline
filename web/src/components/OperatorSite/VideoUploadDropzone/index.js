import React, {Component} from 'react'
import ReactS3Uploader from 'react-s3-uploader-multipart'

import {FETCH_VIDEO} from '../../../actions/video'
import SparkMD5 from 'spark-md5'
import createHash from 'sha.js'

import './index.css'

export default class VideoUploaderDropzone extends Component {
  constructor (props) {
    super(props)
    this.onUploadStart = this.onUploadStart.bind(this)
    this.onProgress = this.onProgress.bind(this)
    this.onUploadError = this.onUploadError.bind(this)
    this.onUploadFinish = this.onUploadFinish.bind(this)

    this.state = {
      video_id: null
    }
  }

  async onUploadStart (file, next) {
    const params = {
      name: file.name,
      content_type: file.type,
      action: FETCH_VIDEO
    }

    let data = await this.props.createVideo(params)
    this.setState({video_id: data.data.video_id}, () => this.props.setUploadingState(true))
    next(file)
  }

  onProgress (percent, status, file, stats) {
    if (stats) {
      const {fileSize, remainingSize} = stats
      let progress = (fileSize - remainingSize) * 100 / fileSize
      this.props.updateProgress(Math.trunc(progress))
    }
  }

  onUploadError () {
    this.props.setUploadingState(false)
    this.props.deleteVideo()
  }

  onUploadFinish () {
    this.props.uploadFinished()
  }

  render () {
    const {access_key, region} = this.props.awsAccount
    const {bucket, signingUrlHeaders} = this.props

    return (
      <div className='dropzone container-fluid text-center'>
        <div className='dropzone-icon'>
          <i className='fas fa-cloud-upload-alt fa-9x' />
          <p>Click here or drop a video file</p>
        </div>
        <ReactS3Uploader
          evaporateOptions={{
            aws_key: access_key,
            bucket: bucket,
            sendCanonicalRequestToSignerUrl: true,
            computeContentMd5: true,
            logging: false,
            region: region,
            contentType: 'video/mp4',
            aws_url: region === 'us-east-1' ? `https://s3.amazonaws.com` : `https://s3-${region}.amazonaws.com`,
            cryptoMd5Method: (data) => btoa(SparkMD5.ArrayBuffer.hash(data, true)),
            cryptoHexEncodedHash256: (data) => createHash('sha256').update(data, 'utf-8').digest('hex'),
          }}
          signingUrl={`/api/v1/videos/signature/`}
          signingUrlHeaders={signingUrlHeaders}
          className='dropzone-input'
          accept='video/*'
          signingUrlWithCredentials={true}
          preprocess={this.onUploadStart}
          onProgress={this.onProgress}
          onError={this.onUploadError}
          onFinish={this.onUploadFinish}
          autoUpload={true}
          uploadRequestHeaders={{'x-amz-acl': 'private'}}
          scrubFilename={() => `${this.state.video_id}/input.mp4`}
        />
      </div>
    )
  }
}

