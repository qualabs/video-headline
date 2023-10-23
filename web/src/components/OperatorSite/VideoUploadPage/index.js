import React, {Component} from 'react'
import {connect} from 'react-redux'
import history from '../../../history'

import Page from '../../Page'
import VideoUploaderDropzone from '../VideoUploadDropzone'
import VideoForm from '../VideoForm'

import {createVideo, deleteVideo, changeVideoStateToQueued} from '../../../actions/video'
import {setMessage} from '../../../actions/flashMessage'

import './index.css'
import {APIHeaders} from '../../../actions/utils'

class VideoUploadPage extends Component {
  constructor (props) {
    super(props)
    this.updateProgress = this.updateProgress.bind(this)
    this.deleteVideo = this.deleteVideo.bind(this)
    this.changeVideoStateToQueued = this.changeVideoStateToQueued.bind(this)
    this.state = {completed: 0, uploading: false, uploadFinished: false}
  }

  updateProgress (percent) {
    this.setState({completed: percent})
  }

  deleteVideo () {
    this.props.deleteVideo(this.props.video.id).then(() => {
      history.push('/drop/')
      this.props.setMessage('Error in video loading, please try again.', 'alert-danger', false)
    })
  }

  changeVideoStateToQueued () {
    this.props.changeVideoStateToQueued(this.props.video.id).then(() => {
      this.setState({uploadFinished: true})
    })
  }

  setUploadingState = (uploading) => {
    this.setState({uploading: uploading})
  }

  render () {
    let channel = null
    const {channel_id} = this.props.match.params
    const {session, createVideo, video} = this.props
    const {organization} = session.user

    if (channel_id) {
      channel = [channel_id]
    }

    if (!organization.upload_enabled) {
      return <Page header={<h1>New Video</h1>}>
        <div className='denied container-fluid text-center'>
          <div className='denied-icon'>
            <i className='fas fa-do-not-enter fa-9x' />
            <p>The organization where you belong is not allowed to upload videos.</p>
          </div>
        </div>
      </Page>
    }

    return (
      <Page header={<h1>New Video</h1>}>
        {!this.state.uploading ?
          <VideoUploaderDropzone
            createVideo={createVideo}
            deleteVideo={this.deleteVideo}
            updateProgress={this.updateProgress}
            onContinue={this.changeVideoStateToQueued}
            uploadFinished={this.changeVideoStateToQueued}
            setUploadingState={this.setUploadingState}
            awsAccount={organization.aws_account}
            bucket={organization.bucket_name}
            organizationId={organization.id}
            signingUrlHeaders={APIHeaders(session)}
          /> :
          <VideoForm
            initialValues={{
              ...video,
              id: video.id,
              channel: channel
            }}
            deleteVideo={this.deleteVideo}
            completed={this.state.completed}
            uploadFinished={this.state.uploadFinished}
          />
        }
      </Page>
    )
  }
}

function mapStateToProps ({video, session, uploadStatus}) {
  return {
    video: video,
    uploadStatus: uploadStatus,
    session: session
  }
}

export default connect(mapStateToProps, {createVideo,
  deleteVideo,
  changeVideoStateToQueued,
  setMessage})(VideoUploadPage)
