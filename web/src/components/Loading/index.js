import React from 'react'
import classnames from 'classnames'
import './index.css'

export default class Loading extends React.Component {
  render () {
    return (
      <div className={classnames('loading', {
        'loading-fullscreen': this.props.fullscreen
      })}>
        <div className='spinner-border' role='status'>
          <span className='sr-only'>Loading...</span>
        </div>
      </div>
    )
  }
}
