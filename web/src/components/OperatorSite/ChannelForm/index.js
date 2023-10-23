import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Field, reduxForm, stopSubmit} from 'redux-form'
import history from '../../../history'

import {fieldRequired, intervalValueLength, isUrlValid} from '../../Form/validators'
import {FormGroup, InputField, CheckboxField} from '../../Form'

import ConfirmButton from '../../ConfirmButton'

import {fetchChannel, createChannel, updateChannel, fetchChannels} from '../../../actions/channel'
import {setMessage} from '../../../actions/flashMessage'

const intervalValueLengthUrl = intervalValueLength(0, 1024)

const CHANNEL_FORM = 'channel_form'

class ChannelForm extends Component {
  handleDelete () {
    const {id} = this.props.initialValues || {}
    if (id) {
      this.props.deleteChannel(id).then(() => {
        this.props.setMessage('Video Group deleted succesfully.', 'success')
      }).catch(e => {
        let msg = e.response.data.detail[0]
        this.props.setMessage(msg, 'error')
      })
    }
  }

  render () {
    const {error, reset, pristine, submitting,
      handleSubmit, initialValues} = this.props
    return (
      <form className='form container-fluid top-buffer' onSubmit={handleSubmit}>
        <div className='row'>
          <div className='col-md-12 offset-xl-3 col-xl-6'>

            <FormGroup labelText='Name'>
              <Field
                name='name'
                component={InputField}
                validate={[fieldRequired]}
              />
            </FormGroup>

            <FormGroup
              labelText='Ads URL'
              helpText='Example: https://www.ads.com'>
              <Field
                name='ads_vast_url'
                component={InputField}
                validate={[isUrlValid, intervalValueLengthUrl]}
              />
            </FormGroup>

            <FormGroup
              labelText='Allowed domains'
              helpText='Register values separated by comma'>
              <Field
                name='allowed_domains'
                component={InputField}
              />
            </FormGroup>

            <FormGroup
              labelText='Detect AdBlock?'
              helpText='If an Ad Block is detected, the user will not be able to reproduce the content.'>
              <Field
                name='detect_adblock'
                component={CheckboxField}
                className='adblock_checkbox'
              />
            </FormGroup>

            <FormGroup
              labelText='Autoplay?'
              helpText='If enabled, playback will start automatically. In some browsers, playback will start with the audio muted.'>
              <Field
                name='autoplay'
                component={CheckboxField}
                className='adblock_checkbox'
              />
            </FormGroup>

            <FormGroup>
              <button
                className='btn btn-primary'
                type='submit'
                disabled={submitting}
              >{submitting ? 'Saving...' : 'Save'}</button>
              <button className='btn btn-outline-secodary' disabled={pristine || submitting} onClick={reset} >Clean</button>
              {initialValues && initialValues.id && (
                <ConfirmButton
                  className='btn btn-danger pull-right'
                  dialogMessage='Delete this video group'
                  handleConfirm={this.handleDelete.bind(this)}
                >Delete</ConfirmButton>
              )}
            </FormGroup>

            {error && (
              <span className='error'>
                <i className='fas fa-fw fa-times'/>
                {error}
              </span>
            )}
          </div>
        </div>
      </form>
    )
  }
}

function onSubmit (values, dispatch, props) {
  let data = {...values}
  // If we need to transform the data, this is the place
  // allowed_domains must be a string array, so...
  if (data.allowed_domains !== undefined) {
    if (data.allowed_domains instanceof Array) {
      data.allowed_domains = data.allowed_domains.toString()
    }
    data.allowed_domains = data.allowed_domains.replace(/^\s*|\s*$/g, '').split(/\s*,\s*/).filter(Boolean)
  }
  if (data.id) {
    return dispatch(updateChannel(data)).then(() => {
      dispatch(fetchChannel(values.id))
      dispatch(fetchChannels())
      history.push(`/video-groups/${data.id}/`)
    })
  } else {
    return dispatch(createChannel(data)).then(data => {
      // Go to the page of the new channel
      dispatch(fetchChannels())
      history.push(`/video-groups/${data.data.id}/`)
    })
  }
}

function onSubmitFail (errors, dispatch, submitError, props) {
  if (submitError != null) {
    if (submitError.response.data.exception === 'ValidationError') {
      dispatch(stopSubmit(CHANNEL_FORM, {_error: submitError.response.data.detail.non_field_errors}))
    } else if (submitError) {
      dispatch(stopSubmit(CHANNEL_FORM, {_error: submitError.response.data.detail}))
    }
  } else if (errors) {
    dispatch(stopSubmit(CHANNEL_FORM, {_error: 'Some fields contain errors.'}))
  }
}

const ChannelFormFormed = reduxForm({
  form: CHANNEL_FORM,
  enableReinitialize: true,
  onSubmit: onSubmit,
  onSubmitFail: onSubmitFail
})(ChannelForm)

export default connect(null, {setMessage})(ChannelFormFormed)
