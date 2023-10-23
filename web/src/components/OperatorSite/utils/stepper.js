import React from 'react'
import { Link } from 'react-router-dom'
import Stepper from 'react-stepper-horizontal'
import { humanizeDate } from '../../../utils/formatDate'

// VIDEO status
export const WAITING_FILE = 'waiting_file'
export const QUEUING_FAILED = 'queuing_failed'
export const QUEUED = 'queued'
export const PROCESSING = 'processing'
export const PROCESSING_FAILED = 'processing_failed'
export const FINISHED = 'finished'
export const FAILED = 'failed'
export const NOT_FINISHED = 'not_finished'

// LIVE VIDEO status
export const ON = 'on'
export const WAITING_INPUT = 'waiting_input'
export const OFF = 'off'
export const STARTING = 'starting'
export const STOPPING = 'stopping'
export const DELETING = 'deleting'

// LIVE VIDEO input status
export const HEALTHY = 'healthy'
export const UNHEALTHY = 'unhealthy'

// LIVE VIDEO CUT status
export const SCHEDULED = 'scheduled'
export const EXECUTING = 'executing'
export const PERFORMED = 'performed'

export function setActiveStep(state) {
  switch (state) {
    case WAITING_FILE:
      return 0
    case QUEUING_FAILED:
      return 1
    case QUEUED:
      return 1
    case PROCESSING:
      return 2
    case PROCESSING_FAILED:
      return 2
    case FINISHED:
      return 3
    default:
      return 0
  }
}

function renderJobPercentComplete(state, jobPercentComplete) {
  let text = 'Processing'

  if (state === PROCESSING) {
    text = jobPercentComplete ? `${text} ${jobPercentComplete}%` : `${text} 0%`
  }

  return (
    <div>{text}</div>
  )
}

export function renderStepper(video) {
  if (video == null || video === undefined) {
    return (
      <div></div>
    )
  }

  return (
    <div>
      <Stepper steps={[
        { title: 'Uploaded' },
        { title: 'In Queue' },
        { title: renderJobPercentComplete(video.state, video.job_percent_complete) },
        { title: 'Ready' }
      ]}
        activeStep={setActiveStep(video.state)}
        defaultColor='#b9b9b9'
        defaultBarColor='#b9b9b9'
        completeColor='#5A937D'
        activeColor={setStateNameColor(video.state)} />
    </div>
  )
}

export function renderLiveStepper(video) {
  if (video == null || video === undefined) {
    return (
      <div></div>
    )
  }
  return (
    <div>
      <Stepper steps={[
        { title: video.state }
      ]}
        activeName={renderStateName(video.state)}
        activeColor={setStateNameColor(video.state)} />
    </div>
  )
}

export function setStateNameColor(state) {
  switch (state) {
    case STOPPING:
    case WAITING_INPUT:
    case STARTING:
      return '#B57628'

    case QUEUING_FAILED:
    case PROCESSING_FAILED:
    case OFF:
    case EXECUTING:
    case UNHEALTHY:
      return '#c1526f'

    case QUEUED:
    case FINISHED:
    case ON:
    case PERFORMED:
    case HEALTHY:
      return '#5A937D'

    case WAITING_FILE:
    case PROCESSING:
    case SCHEDULED:
      return '#638DB0'
    case DELETING:
      return '#B57628'
    default:
      return '#ffffff'
  }
}

export function renderCircle(state, text, withDotsState = true) {
  return (
    <>
      {withDotsState && (
        <i className='fas fa-circle mr-2' style={{ color: setStateNameColor(state) }} />
      )}
      {text}
    </>
  )
}

export function renderStateName(state) {
  switch (state) {
    case WAITING_FILE:
      return renderCircle(state, 'Uploading File')
    case QUEUING_FAILED:
      return renderCircle(state, 'Enqueue Failed')
    case QUEUED:
      return renderCircle(state, 'In Queue')
    case PROCESSING:
      return renderCircle(state, 'Processing')
    case PROCESSING_FAILED:
      return renderCircle(state, 'Failing in processing')
    case FINISHED:
      return renderCircle(state, 'Finished')
    case ON:
      return renderCircle(state, 'On')
    case WAITING_INPUT:
      return renderCircle(ON, 'On')
    case OFF:
      return renderCircle(state, 'Off')
    case STARTING:
      return renderCircle(state, 'Starting')
    case STOPPING:
      return renderCircle(state, 'Stopping')
    case SCHEDULED:
      return renderCircle(state, 'Scheduled')
    case EXECUTING:
      return renderCircle(state, 'In Progress')
    case PERFORMED:
      return renderCircle(state, 'Completed')
    case DELETING:
      return renderCircle(state, 'Deleting')
    default:
      return 0
  }
}

export function renderInputState(state, withDotsState = true) {
  if (state.length > 0) {
    if (state.length === 1) return renderCircle(UNHEALTHY, `${state.length} alert`, withDotsState)
    return renderCircle(UNHEALTHY, `${state.length} alerts`, withDotsState)
  } else {
    return renderCircle(HEALTHY, 'Receiving', withDotsState)
  }
}

export function renderSimpleInputState(video, withDotsState = true) {
  if (video.state === WAITING_INPUT) {
    return renderCircle(WAITING_INPUT, `Waiting input`, withDotsState)
  } else if (video.input_state.length > 0) {
    return renderCircle(UNHEALTHY, `With alerts`, withDotsState)
  } else {
    return renderCircle(HEALTHY, 'Receiving', withDotsState)
  }
}

export function renderCutState(cut, id) {
  if (cut != null) {
    return (
      <div>
        <Link className='alert-summary-primary' to={`/live-videos/${id}/cuts/${cut.id}`}>
          Description: {cut.description}, is restored: {humanizeDate(cut.final_time)}
        </Link>
      </div>
    )
  }
}
