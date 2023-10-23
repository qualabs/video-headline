import React from 'react'
import {Alert} from 'react-bootstrap'


export default class CustomAlert extends React.Component {

  render () {
    const {className, alertType, dismissFunction} = this.props
    return (
      <Alert
        bsClass={className}
        bsStyle={alertType}
        onDismiss={dismissFunction}
      >
        {this.props.children}
      </Alert>
    )
  }
}
