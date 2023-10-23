import React, {Component} from 'react'
import {confirmAlert} from 'react-confirm-alert'

import 'react-confirm-alert/src/react-confirm-alert.css'
import './index.css'

export default class ConfirmButton extends Component {
  confirmDialogDelete () {
    const {dialogTitle, dialogMessage, dialogButton, handleConfirm} = this.props

    confirmAlert({
      customUI: ({onClose}) => {
        return (
          <div className='modal-dialog modal-dialog-centered' role='document'>
            <div className='modal-content'>
              <div className='modal-header'>
                <h5 className='modal-title' id='exampleModalCenterTitle'>{dialogTitle || '¿Are you sure?'}</h5>
                <button
                  type='button'
                  className='close'
                  data-dismiss='modal'
                  aria-label='Close'
                  onClick={onClose}>
                  <span aria-hidden='true'>&times;</span>
                </button>
              </div>
              <div className='modal-body'>
                {dialogMessage}
              </div>
              <div className='modal-footer'>
                <button
                  type='button'
                  className='btn btn-secondary'
                  data-dismiss='modal'
                  onClick={onClose}>
                    No
                </button>
                <button
                  type='button'
                  className='btn btn-primary'
                  onClick={() => {
                    handleConfirm()
                    onClose()
                  }}>
                  {dialogButton || 'Yes, sure'}
                </button>
              </div>
            </div>
          </div>
        )
      },
    })
  }

  render () {
    const {className, disable} = this.props

    return (
      <button
        type='button'
        className={`${className} ${disable ? 'without-hover' : ''}`}
        onClick={this.confirmDialogDelete.bind(this)}
        disabled={disable}
      >
        {this.props.children}
      </button>
    )
  }
}
