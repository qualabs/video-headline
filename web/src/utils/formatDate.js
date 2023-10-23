import moment from 'moment'
import 'moment/locale/en-gb'

moment.locale('en-gb')

export function toNumericDate (date) {
  let new_date = new Date(date)
  return Intl.DateTimeFormat('en-gb', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: 'numeric',
    minute: '2-digit'
  }).format(new_date)
}

export function toNumericTime (date) {
  let new_date = new Date(date)

  if (new_date.getHours() === 0 && new_date.getMinutes() === 0) {
    return toNumericDate(date)
  }
  return Intl.DateTimeFormat('en-gb', {
    hour: 'numeric',
    minute: '2-digit'
  }).format(new_date)
}


export function toNumericMonth (date) {
  let new_date = new Date(`${date}T00:00:00`)
  return Intl.DateTimeFormat('en-gb', {
    month: 'long',
    year: 'numeric'
  }).format(new_date)
}

export function toNumericDateNoTime (date) {
  let new_date = moment(date)
  return Intl.DateTimeFormat('en-gb', {
    month: 'short',
    day: '2-digit'
  }).format(new_date)
}

export function secondsToMinutes (seconds) {
  let mins = Math.floor(seconds / 60)
  let secs = seconds % 60
  return secs < 10 ? `${mins}:0${secs}` : `${mins}:${secs}`
}

function formatNumber (number) {
  if (number < 10) {
    number = `0${number}`
  }

  return number
}

export function convertDHMS (seconds) {
  if (isNaN(seconds)) {
    return null
  }

  const SECONDS_IN_DAY = 86400
  const SECONDS_IN_HOUR = 3600
  const SECONDS_IN_MINUTE = 60

  let daysCount = Math.floor(seconds / SECONDS_IN_DAY)
  let hoursCount = formatNumber(Math.floor((seconds % SECONDS_IN_DAY) / SECONDS_IN_HOUR))
  let minutesCount = formatNumber(Math.floor(((seconds % SECONDS_IN_DAY) % SECONDS_IN_HOUR) / SECONDS_IN_MINUTE))
  let secondsCount = formatNumber(((seconds % SECONDS_IN_DAY) % SECONDS_IN_HOUR) % SECONDS_IN_MINUTE)

  if (seconds >= SECONDS_IN_DAY) {
    return (
      `${daysCount}d ${hoursCount}:${minutesCount}:${secondsCount}`
    )
  }

  return (
    `${hoursCount}:${minutesCount}:${secondsCount}`
  )
}

export function humanizeDate (date) {
  let initialTime = moment(new Date(date))
  let today = moment(new Date())
  return initialTime.calendar(today, {
    sameDay: '[Today at] HH:mm',
    lastDay: '[Yesterday at] HH:mm',
    lastWeek: '[Last] dddd [at] HH:mm',
    sameElse: 'DD/MM/YYYY HH:mm'
  })
}
