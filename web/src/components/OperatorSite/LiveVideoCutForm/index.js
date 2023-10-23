import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Field, reduxForm, stopSubmit} from 'redux-form'
import history from '../../../history'

import {fieldRequired} from '../../Form/validators'
import {FormGroup, InputField, DateTimePickerField} from '../../Form'

import ConfirmButton from '../../ConfirmButton'

import {fetchLiveVideoCut, createLiveVideoCut, updateLiveVideoCut, deleteLiveVideoCut} from '../../../actions/cuts'
import {setMessage} from '../../../actions/flashMessage'
import {SCHEDULED} from '../utils/stepper'

const CUT_FORM = 'cut_form'

class LiveVideoCutForm extends Component {
  handleDelete () {
    const {live} = this.props.initialValues
    const {id} = this.props.initialValues || {}
    if (id) {
      this.props.deleteLiveVideoCut(id).then(() => {
        history.push(`/live-videos/${live}/cuts/`)
        this.props.setMessage('Cut deleted correctly.', 'success')
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
            <FormGroup labelText='Cut description'>
              <Field
                name='description'
                component={InputField}
                validate={[fieldRequired]}
              />
            </FormGroup>
            <FormGroup
              labelText='Start Date and Hour'>
              <Field
                name='initial_time'
                disabled={initialValues.state && initialValues.state !== SCHEDULED}
                component={DateTimePickerField}
                validate={[fieldRequired]}
              />
            </FormGroup>
            <FormGroup
              labelText='End Date and Hour'>
              <Field
                name='final_time'
                component={DateTimePickerField}
                validate={[fieldRequired]}
              />
            </FormGroup>
            <FormGroup>
              <button className='btn btn-primary' type='submit'>Save</button>
              <button className='btn btn-outline-secodary' disabled={pristine || submitting} onClick={reset} >Clean</button>
              {initialValues && initialValues.id && initialValues.state === SCHEDULED && (
                <ConfirmButton
                  className='btn btn-danger pull-right'
                  dialogMessage='Delete this cut?'
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

function onSubmit (values, dispatch) {
  let data = {...values}

  if (data.id) {
    return dispatch(updateLiveVideoCut(data)).then(() => {
      history.push(`/live-videos/${data.live}/cuts/`)
    })
  } else {
    return dispatch(createLiveVideoCut(data)).then(data => {
      history.push(`/live-videos/${data.data.live}/cuts/`)
    })
  }
}

function onSubmitFail (errors, dispatch, submitError) {
  if (submitError) {
    dispatch(stopSubmit(CUT_FORM, {_error: submitError.response.data[0]}))
  } else if (errors) {
    dispatch(stopSubmit(CUT_FORM, {_error: 'Some fields contain errors.'}))
  }
}

const LiveVideoCutFormFormed = reduxForm({
  form: CUT_FORM,
  enableReinitialize: true,
  onSubmit: onSubmit,
  onSubmitFail: onSubmitFail,
  asyncBlurFields: ['description']
})(LiveVideoCutForm)


export default connect(null, {fetchLiveVideoCut,
  setMessage,
  deleteLiveVideoCut})(LiveVideoCutFormFormed)
