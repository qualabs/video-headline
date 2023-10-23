import React, {Component} from 'react'
import {connect} from 'react-redux'

import {updateVideo} from '../../../actions/video'
import {deleteThumbnail} from '../../../actions/thumb'
import {setMessage} from '../../../actions/flashMessage'

import ReactS3Uploader from 'react-s3-uploader-qualabs'

import './index.css'

class ThumbnailUploader extends Component {
  constructor (props) {
    super(props)

    this.uploader = null
    this.uploadInput = null

    this.onUploadFinish = this.onUploadFinish.bind(this)
    this.getSignedUrl = this.getSignedUrl.bind(this)

    this.state = {
      finishedUploading: false,
      hasThumbnail: props.hasThumbnail,
      deleteButton: props.hasThumbnail,
      thumbnailPreview: null
    }
  }

  componentWillUnmount () {
    URL.revokeObjectURL(this.state.thumbnailPreview)
  }

  handleUpload = () => {
    this.uploader.uploadFile()
    this.props.setLoading(true)

    return new Promise((resolve) => {
      let interval = setInterval(() => {
        if (this.state.finishedUploading) {
          clearInterval(interval)
          this.props.setLoading(false)
          resolve()
        }
      }, 500)
    })
  }

  async getSignedUrl (file, callback) {
    let {data} = await this.props.getThumbnailSignedUrl(this.props.videoId, file.type)
    callback({signedUrl: data.signed_url})
  }

  onUploadFinish () {
    let data = {
      id: this.props.videoId,
      has_thumbnail: true
    }

    this.props.updateVideo(data)
    this.setState({finishedUploading: true})
  }

  handleDeleteThumbnail (e, videoId) {
    e.preventDefault()
    this.uploader.clear()

    URL.revokeObjectURL(this.state.thumbnailPreview)
    this.setState({deleteButton: false, thumbnailPreview: null})

    if (this.state.hasThumbnail) {
      this.props.setLoading(true)
      this.props.deleteThumbnail(videoId).then(() => {
        this.props.setMessage('Thumbnail was deleted correctly.', 'success')
        this.props.setLoading(false)
        this.setState({hasThumbnail: false})
      })
    }

  }

  checkHasThumbnailFileSelected = () => {
    if (this.uploadInput && this.uploadInput.value) {
      return true
    }

    return false
  }

  setUploader = (uploader) => {
    this.uploader = uploader
  }

  setPreviewValue = (input) => {
    let file = input.files[0]
    const bloblUrl = URL.createObjectURL(file)

    if (this.uploadInput && this.uploadInput.value) {
      this.setState({thumbnailPreview: bloblUrl})
    }
  }

  renderDropzoneContent = () => {
    if (this.state.deleteButton) {
      return (
      <>
        {this.renderPreview()}
        </>
      )
    } else {
      return (
        <>
        <i className='fas fa-cloud-upload-alt fa-5x upload-icon' />
            <p>Click here or drop an image</p>
        </>
      )
    }
  }

  renderPreview = () => {
    let src

    if (this.props.hasThumbnail && !this.checkHasThumbnailFileSelected()) {
      src = this.props.previewUrl
    } else {
      src = this.state.thumbnailPreview
    }

    return (
      <img id='thumbnail-preview' src={src} alt='Uploaded thumbnail preview'/>
    )
  }

  handleOnChange = (input) => {
    this.setState({deleteButton: this.checkHasThumbnailFileSelected()})
    this.setPreviewValue(input)

    if (this.state.thumbnailPreview) {
      URL.revokeObjectURL(this.state.thumbnailPreview)
    }
  }

  render () {
    const {videoId} = this.props

    return (
      <div className='image-dropzone row'>
        <div className='thumb-dropzone container-fluid text-center'>
          <div className='dropzone-icon'>
            {this.renderDropzoneContent()}
          </div>
          <ReactS3Uploader
            className='dropzone-input'
            getSignedUrl={this.getSignedUrl}
            accept='image/*'
            onSignedUrl={this.onSignedUrl}
            onFinish={this.onUploadFinish}
            autoUpload={false}
            ref={uploader => this.setUploader(uploader)}
            inputRef={cmp => this.uploadInput = cmp}
            uploadRequestHeaders={{'x-amz-acl': 'public-read'}}
            scrubFilename={() => 'thumb.jpg'}
            onChange={(event) => this.handleOnChange(event.target)}
          />
        </div>
        { this.state.deleteButton &&
          <div className='div-delete-thumb'>
            <button
              className='btn btn-delete-thumb'
              onClick={(e) => this.handleDeleteThumbnail(e, videoId)}
            >
              <i className='fas fa-trash-alt'/>
              <span>Delete image</span>
            </button>
          </div>
        }
      </div>
    )
  }
}

export default connect(null, {updateVideo, deleteThumbnail, setMessage}, null, {withRef: true})(ThumbnailUploader)
