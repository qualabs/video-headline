import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Field, reduxForm, stopSubmit } from 'redux-form'
import history from '../../../history'

import { fieldRequired, isUrlValid, intervalValueLength } from '../../Form/validators'
import { WAITING_FILE } from '../utils/stepper'
import { FormGroup, InputField, ObjectMultiselectField, CheckboxField, DropDownListField, ObjectDropDownListField } from '../../Form'

import ConfirmButton from '../../ConfirmButton'
import { ProgressBar } from 'react-bootstrap'

import debounce from 'lodash/debounce'

import { createVideo, updateVideo } from '../../../actions/video'
import { fetchTags } from '../../../actions/tags'
import { fetchChannels } from '../../../actions/channel'
import { setMessage } from '../../../actions/flashMessage'
import { deleteVideo } from '../../../actions/video'

import ThumbnailUploader from '../ThumbnailUploader'
import { getThumbnailSignedUrl, deleteThumbnail } from '../../../actions/thumb'

import './index.css'

const intervalValueLengthUrl = intervalValueLength(0, 1024)

const VIDEO_FORM = 'video_form'

class VideoForm extends Component {
  constructor(props) {
    super(props)
    this.onSearchChange = debounce(this.onSearchChange.bind(this), 500)
    this.customUploader = null
    this.state = {
      loadingThumbnail: false
    }
  }

  onSearchChange(search) {
    this.props.fetchTags({ search })
  }

  componentDidMount() {
    this.props.fetchTags()
    this.props.fetchChannels()
  }

  handleDelete() {
    const { id } = this.props.initialValues || {}
    if (id) {
      this.props.deleteVideo(id).then(() => {
        history.push('/video-on-demand/')
        this.props.setMessage('Video deleted correctly.', 'success')
      }).catch(e => {
        let msg = e.response.data.detail[0]
        this.props.setMessage(msg, 'error')
      })
    }
  }

  formatTags(tags) {
    let names = tags.map(function (item) {
      return item['name']
    })

    return names
  }

  renderUploadProgressBar(state) {
    if (state === WAITING_FILE) {
      return (
        <FormGroup labelText='Loading process'>
          <ProgressBar
            status='error'
            now={this.props.completed}
            label={this.props.uploadFinished ? 'Completed' : `${this.props.completed}%`}
          />
        </FormGroup>
      )
    } else {
      return null
    }
  }

  renderThumbnailUploader = (id, videoId, hasThumbnail) => {

    const { videoChannel } = this.props

    if (videoChannel) {
      return (
        <FormGroup
          labelText='Thumbnail'>
          <ThumbnailUploader
            videoId={id}
            ref={element => this.customUploader = element}
            getThumbnailSignedUrl={this.props.getThumbnailSignedUrl}
            hasThumbnail={hasThumbnail}
            setLoading={this.setLoadingThumbnail}
            previewUrl={`https://${videoChannel.cf_domain}/${videoId}/thumb.jpg`}
          />
        </FormGroup>
      )
    }

    return null
  }

  handleSubmit = (values, dispatch) => {
    const uploader = this.customUploader ? this.customUploader.getWrappedInstance() : null

    if (uploader && uploader.uploadInput.value) {
      uploader.handleUpload().then(() => onSubmit(values, dispatch))
    } else {
      onSubmit(values, dispatch)
    }
  }

  setLoadingThumbnail = (loading) => {
    this.setState({ loadingThumbnail: loading })
  }

  render() {
    const { error, reset, pristine, submitting,
      handleSubmit, tags, channels, initialValues,
      hasThumbnail } = this.props

    const uploadCompleted = this.props.uploadFinished

    return (
      <form className='form container-fluid top-buffer' onSubmit={handleSubmit(this.handleSubmit)}>
        <div className='row'>
          <div className='col-md-12 offset-xl-3 col-xl-6'>

            <FormGroup labelText='Name'>
              <Field
                name='name'
                component={InputField}
                validate={[fieldRequired]}
              />
            </FormGroup>

            <FormGroup labelText='Video Group'>
              <Field
                name='channel'
                component={ObjectDropDownListField}
                filter='contains'
                data={channels ? channels.results : []}
                textField='name'
                valueField='id'
                validate={[fieldRequired]}
              />
            </FormGroup>

            <FormGroup labelText='Tags'>
              <Field
                name='tags'
                component={ObjectMultiselectField}
                filter='contains'
                data={tags ? tags.results : []}
                textField='name'
                valueField='name'
                allowCreate='onFilter'
                onSearch={this.onSearchChange.bind(this)}
              />
            </FormGroup>

            <FormGroup
              labelText='Ads Vast Url'
              helpText='Example: https://www.ads.com'>
              <Field
                name='ads_vast_url'
                component={InputField}
                validate={[isUrlValid, intervalValueLengthUrl]}
              />
            </FormGroup>

            <FormGroup
              labelText='Enable ads?'
              helpText='If disabled, the video will not show advertising of any kind.'>
              <Field
                name='enable_ads'
                component={CheckboxField}
                className='ads_checkbox'
              />
            </FormGroup>

            <FormGroup
              labelText='Autoplay?'
              helpText='If enabled, the video will start automatically. In some browsers playback will start with the audio muted.'>
              <Field
                name='autoplay'
                data={['c', 'y', 'n']}
                textField={(d) => {
                  const labels = {
                    'y': 'Yes',
                    'n': 'No',
                    'c': 'According to video group configuration'
                  }
                  return labels[d]
                }}
                component={DropDownListField}
              />
            </FormGroup>

            {this.renderThumbnailUploader(initialValues.id, initialValues.video_id, hasThumbnail)}

            {this.renderUploadProgressBar(initialValues.state)}
            {
              // TODO: Fix disabled condition, not working as expected, but working anyways
              // button is enabled when starting to upload video and instantly gets disabled
            }
            <FormGroup>
              <button
                className='btn btn-primary'
                type='submit'
                disabled={(!uploadCompleted && initialValues.state === WAITING_FILE) || this.state.loadingThumbnail}
              >Save</button>
              <button className='btn btn-outline-secodary' disabled={pristine || submitting} onClick={reset} >Clean</button>
              {initialValues && initialValues.id && (
                <ConfirmButton
                  className='btn btn-danger pull-right'
                  dialogMessage='Delete this video'
                  handleConfirm={this.handleDelete.bind(this)}
                >Delete</ConfirmButton>
              )}
            </FormGroup>
            {error && (
              <span className='error'>
                <i className='fas fa-fw fa-times' />
                {error}
              </span>
            )}
          </div>
        </div>
      </form>
    )
  }
}

function onSubmit(values, dispatch) {
  let data = { ...values }

  if (data.id) {
    return dispatch(updateVideo(data)).then(() => {
      history.push(`/video-on-demand/${data.id}/`)
    })
  } else {
    return dispatch(createVideo(data)).then(data => {
      history.push(`/video-on-demand/${data.data.id}/`)
    })
  }
}

function onSubmitFail(errors, dispatch, submitError) {
  if (submitError) {
    dispatch(stopSubmit(VIDEO_FORM, { _error: submitError.response.data.non_field_errors[0] }))
  } else if (errors) {
    dispatch(stopSubmit(VIDEO_FORM, { _error: 'Some fields contain errors.' }))
  }
}

const VideoFormFormed = reduxForm({
  form: VIDEO_FORM,
  enableReinitialize: true,
  onSubmit: onSubmit,
  onSubmitFail: onSubmitFail
})(VideoForm)

function mapStateToProps({ list, video }) {
  return {
    tags: list.tags,
    channels: list.channels,
    hasThumbnail: video.has_thumbnail,
    videoChannel: video.channel
  }
}

export default connect(mapStateToProps,
  {
    fetchTags,
    fetchChannels,
    setMessage,
    deleteVideo,
    getThumbnailSignedUrl,
    deleteThumbnail
  })(VideoFormFormed)
