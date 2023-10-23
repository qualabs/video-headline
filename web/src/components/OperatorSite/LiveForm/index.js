import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Field, reduxForm, stopSubmit, formValueSelector} from 'redux-form'
import history from '../../../history'
import Loading from '../../Loading'

import {
  fieldRequired,
  isUrlValid,
  intervalValueLength,
} from '../../Form/validators'

import {
  FormGroup,
  InputField,
  ObjectMultiselectField,
  CheckboxField,
  ObjectDropDownListField,
  DropDownListField,
} from '../../Form'

import debounce from 'lodash/debounce'

import {isoCountries, geoType} from '../../../utils/isoCountries'

import {
  createLiveVideo,
  fetchLiveVideo,
  fetchLiveVideos,
  updateLiveVideo,
} from '../../../actions/live'
import {fetchTags} from '../../../actions/tags'
import {fetchChannels} from '../../../actions/channel'

import './index.css'

const intervalValueLengthUrl = intervalValueLength(0, 1024)

const LIVE_FORM = 'live_form'

class LiveForm extends Component {
  constructor (props) {
    super(props)
    this.onSearchChange = debounce(this.onSearchChange.bind(this), 500)
  }

  onSearchChange (search) {
    this.props.fetchTags({search})
  }

  componentDidMount () {
    this.props.fetchTags()
    this.props.fetchChannels()
  }

  componentDidUpdate () {
    this.props.fetchChannels()
  }

  formatTags (tags) {
    let names = tags.map(function (item) {
      return item['name']
    })

    return names
  }

  render () {
    const {
      error,
      reset,
      pristine,
      submitting,
      handleSubmit,
      tags,
      channels,
      geolocationEnabled,
      submitSucceeded,
    } = this.props

    if (submitting && !submitSucceeded) {
      return <Loading />
    }

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
              labelText='Advertising URL'
              helpText='Example: https://www.advertising.com'
            >
              <Field
                name='ads_vast_url'
                component={InputField}
                validate={[isUrlValid, intervalValueLengthUrl]}
              />
            </FormGroup>

            <FormGroup
              labelText='Enable ads?'
              helpText='If disabled, the video will not show advertising of any kind'
            >
              <Field
                name='enable_ads'
                component={CheckboxField}
                className='ads_checkbox'
              />
            </FormGroup>

            <FormGroup
              labelText='Autoplay?'
              helpText='If enabled, the video will start automatically. In some browsers, playback will start with the audio muted.'>
              <Field
                name='autoplay'
                data={['c', 'y', 'n']}
                textField={(d) => {
                  const labels = {
                    y: 'Yes',
                    n: 'No',
                    c: 'According to video group configuration',
                  }
                  return labels[d]
                }}
                component={DropDownListField}
              />
            </FormGroup>

            <FormGroup labelText='Geolocation type'>
              <Field
                name='geolocation_type'
                id='geolocation_type'
                component={ObjectDropDownListField}
                data={geoType}
                textField='name'
                valueField='id'
              />
            </FormGroup>

            {geolocationEnabled && (
              <FormGroup labelText='Countries'>
                <Field
                  name='geolocation_countries'
                  component={ObjectMultiselectField}
                  filter='contains'
                  data={isoCountries}
                  textField='name'
                  valueField='id'
                  onSearch={this.onSearchChange.bind(this)}
                />
              </FormGroup>
            )}

            <FormGroup>
              <button className='btn btn-primary' type='submit'>
                Save
              </button>
              <button
                className='btn btn-outline-secodary'
                disabled={pristine || submitting}
                onClick={reset}
              >
                Clean
              </button>
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

function onSubmit (values, dispatch) {
  let data = {...values}
  if (data.id) {
    return dispatch(updateLiveVideo(data)).then(() => {
      history.push(`/live-videos/${data.id}/`)
    })
  } else {
    return dispatch(createLiveVideo(data)).then((data) => {
      // Go to the page of the new channel
      dispatch(fetchLiveVideos())
      history.push(`/live-videos/${data.data.id}/`)
    })
  }
}

function onSubmitFail (errors, dispatch, submitError) {
  if (submitError) {
    dispatch(
      stopSubmit(LIVE_FORM, {
        _error: submitError.response.data.non_field_errors[0],
      })
    )
  } else if (errors) {
    dispatch(stopSubmit(LIVE_FORM, {_error: 'Some fields contain errors.'}))
  }
}

function asyncValidate (values, dispatch) {
  let data = {...values}
  if (data.id) {
    return dispatch(updateLiveVideo(data)).then(() => {
      dispatch(fetchLiveVideo(data.id))
      history.push(`/live-videos/${data.id}/`)
    })
  } else {
    return Promise.resolve()
  }
}

const LiveFormFormed = reduxForm({
  form: LIVE_FORM,
  enableReinitialize: true,
  onSubmit: onSubmit,
  onSubmitFail: onSubmitFail,
  asyncValidate,
  asyncBlurFields: ['name'],
})(LiveForm)

const selector = formValueSelector(LIVE_FORM)

function mapStateToProps (state) {
  const geolocationType = selector(state, 'geolocation_type')
  return {
    geolocationEnabled: geolocationType !== 'none',
    tags: state.list.tags,
    channels: state.list.channels,
  }
}

export default connect(mapStateToProps, {
  fetchTags,
  fetchChannels,
})(LiveFormFormed)
