import React, {Component} from 'react'
import {Field, reduxForm} from 'redux-form'
import {FormGroup, InputField} from '../../../Form'

import {login} from '../../../../actions/user'

import '../../styles/index.css'

class LoginForm extends Component {

  render () {
    const {error, handleSubmit} = this.props
    return (
      <form onSubmit={handleSubmit}>
        <div className='container-fluid'>
          <div className='form-row'>
            <div className='col-xs-12'>
              <FormGroup labelText='User'>
                <Field
                  name='username'
                  component={InputField}
                />
              </FormGroup>

              <FormGroup labelText='Password'>
                <Field
                  name='password'
                  type='password'
                  component={InputField}
                />
              </FormGroup>

              <FormGroup className='col-xs-12'>
                <button className='btn btn-primary' type='submit'>Login</button>
              </FormGroup>
              <div className='error'>
                {error && <small>{error}</small>}
              </div>
            </div>
          </div>
        </div>

      </form>
    )
  }
}

function onSubmit (values, dispatch) {
  dispatch(login(values))
}

function validate (values) {
  let ret = {}
  if (!values.username) {
    ret = {...ret, username: 'Required'}
  }
  if (!values.password) {
    ret = {...ret, password: 'Required'}
  }
  return ret
}

export default reduxForm({
  // a unique name for the form
  form: 'login',
  onSubmit: onSubmit,
  validate: validate
})(LoginForm)
