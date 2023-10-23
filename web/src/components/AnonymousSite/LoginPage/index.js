import React, {Component} from 'react'
import LoginForm from './LoginForm'

import FlashMessage from '../../FlashMessage'

import {getLogo} from '../../../utils/logo'

export default class Login extends Component {
  componentDidMount () {
    document.body.classList.add('annon-page')
  }

  componentWillUnmount () {
    document.body.classList.remove('annon-page')
  }

  render () {
    return [
      <FlashMessage key='flash-message-login'/>,
      <div className='container-fluid index' key='div-login'>
        <div className='annon-form'>
          {getLogo()}
          <LoginForm />
        </div>
      </div>
    ]
  }
}
