import React from 'react'

import {ProgressBar} from 'react-bootstrap'

export default function CustomProgressBar (props) {
  if (props.maxValue) {
    return (
      <>
      <ProgressBar now={props.value * 100 / props.maxValue} />
        {props.value}/{props.maxValue} {props.units}
      </>
    )
  } else {
    return (
      <span>
        {props.value} {props.units}
      </span>
    )
  }
}
