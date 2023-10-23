import React, {Component} from 'react'
import {connect} from 'react-redux'
import history from '../../../history'

import Page from '../../Page'
import AudioUploaderDropzone from '../AudioUploadDropzone'
import VideoForm from '../VideoForm'

import {createVideo, deleteVideo, changeVideoStateToQueued} from '../../../actions/video'
import {setMessage} from '../../../actions/flashMessage'

import './index.css'

class AudioUploadPage extends Component {
  constructor (props) {
    super(props)
    this.updateProgress = this.updateProgress.bind(this)
    this.deleteVideo = this.deleteVideo.bind(this)
    this.changeVideoStateToQueued = this.changeVideoStateToQueued.bind(this)
    this.state = {completed: 0, uploadFinished: false}
  }

  updateProgress (percent) {
    this.setState({completed: percent})
  }

  deleteVideo () {
    this.props.deleteVideo(this.props.video.id).then(() => {
      history.push('/drop/')
      this.props.setMessage('Error while loading video, try again.', 'alert-danger', false)
    })
  }

  changeVideoStateToQueued () {
    this.props.changeVideoStateToQueued(this.props.video.id).then(() => {
      this.setState({uploadFinished: true})
    })
  }

  render () {
    let channel = null
    const {isAudio} = this.props

    const {channel_id} = this.props.match.params
    const pageHeader = isAudio ? 'Audio' : 'Video'
    if (channel_id) {
      channel = [channel_id]
    }

    if (!this.props.organization.upload_enabled) {
      return <Page header={<h1>{`New ${pageHeader}`}</h1>}>
        <div className='denied container-fluid text-center'>
          <div className='denied-icon'>
            <i className='fas fa-do-not-enter fa-9x' />
            <p>Your organization is not allowed to upload videos.</p>
          </div>
        </div>
      </Page>
    }
    return (
      <Page header={<h1>{`New ${pageHeader}`}</h1>}>
        {!this.props.video ?
          <AudioUploaderDropzone
            createVideo={this.props.createVideo}
            deleteVideo={this.deleteVideo}
            updateProgress={this.updateProgress}
            onContinue={this.changeVideoStateToQueued}
            uploadFinished={this.changeVideoStateToQueued}
            isAudio={isAudio}
          /> :
          <VideoForm
            initialValues={{
              ...this.props.video,
              id: this.props.video.id,
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

function mapStateToProps ({video, session}) {
  return {
    video: video,
    organization: session.user.organization
  }
}

export default connect(mapStateToProps, {createVideo,
  deleteVideo,
  changeVideoStateToQueued,
  setMessage})(AudioUploadPage)
