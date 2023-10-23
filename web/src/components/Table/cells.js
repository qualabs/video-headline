import React from 'react'

import moment from 'moment'
import 'moment/locale/en-gb'

moment.locale('en-gb')

export function BoolCell (props) {
  if (props.value) {
    return <span className='bool'><i className='fas fa-check'/></span>
  }
  return <span className='bool'><i className='fas fa-times'/></span>
}

export function ArrayCell (props) {
  return <span className='array'>{props.value.join(', ')}</span>
}

export function DateTimeCell (props) {
  return <span className='datetime'>{moment(props.value).format('LLL')}</span>
}
