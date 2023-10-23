import React, {Component} from 'react'
import {connect} from 'react-redux'

import {removeFlashMessage} from '../../actions/flashMessage'

import './index.css'

const MESSAGE_TTL = 10 * 1000

class FlashMessage extends Component {

  componentDidMount () {
    this.time = window.setTimeout(() => {
      this.props.removeFlashMessage()
    }, MESSAGE_TTL)
  }

  componentDidUpdate () {
    if (this.props.flashMessage.message) {
      this.componentDidMount()
    }
  }

  componentWillUnmount () {
    window.clearTimeout(this.time)
  }

  render () {
    const {message, type} = this.props.flashMessage
    if (message) {
      return (
        <div className={`flash-message-container ${type}`} onClick={() => {this.props.removeFlashMessage()}}>
          <span>{message}</span>
          <div onClick={() => {this.props.removeFlashMessage()}} className='button'><i className='fas fa-fw fa-times'></i></div>
        </div>
      )
    } else {
      return null
    }
  }
}

function mapStateToProps ({flashMessage}) {
  return {flashMessage}
}

export default connect(mapStateToProps, {removeFlashMessage})(FlashMessage)
