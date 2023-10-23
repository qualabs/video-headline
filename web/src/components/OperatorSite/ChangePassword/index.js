import React, {Component} from 'react'
import {Field, reduxForm} from 'redux-form'

import {FormGroup} from '../../Form'
import {InputField} from '../../Form'
import Page from '../../Page'
import {fieldRequired} from '../../Form/validators'

import {changePassword} from '../../../actions/user'

const CHANGE_PASSWORD_FORM = 'change-password'

class ChangePassword extends Component {
  render () {
    return (
      <Page header={<h1>My account</h1>}>
        {this.renderForm()}
      </Page>
    )
  }

  renderForm () {
    const {error, handleSubmit} = this.props

    return (
      <div className='container-fluid top-buffer'>
        <h2 className='col-sm-12'>Change password</h2>
        <form className='orm container-fluid top-buffer' onSubmit={handleSubmit}>
          <div className='row'>
            <div className='col-md-12 offset-xl-3 col-xl-6'>
              <FormGroup labelText='Current password'>
                <Field
                  name='old_password'
                  type='password'
                  component={InputField}
                  validate={[fieldRequired]}
                />
              </FormGroup>

              <FormGroup labelText='New password'>
                <Field
                  name='new_password'
                  type='password'
                  component={InputField}
                  validate={[fieldRequired]}
                />
              </FormGroup>

              <FormGroup labelText='Repeat new password'>
                <Field
                  name='new_password_2'
                  type='password'
                  component={InputField}
                  validate={[fieldRequired]}
                />
              </FormGroup>

              <FormGroup>
                <button className='btn btn-primary' type='submit'>Save</button>
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
      </div>
    )
  }
}

function validate (values) {
  let ret = {}
  if (values.new_password !== values.new_password_2) {
    ret = {...ret, _error: 'Passwords do not match.'}
  }
  return ret
}

function onSubmit (values, dispatch) {
  dispatch(changePassword(values))
}

const ChangePasswordForm = reduxForm({
  form: CHANGE_PASSWORD_FORM,
  onSubmit: onSubmit,
  validate: validate
})(ChangePassword)

export default ChangePasswordForm
