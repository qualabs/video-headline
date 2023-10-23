export const fieldRequired = value => value || typeof value === 'number' ? undefined : 'Required'

export const valueLength = length => value => value && value.length === length ? undefined : `This field must be of length ${length}`

export const isUrlValid = value => !value || value.match(/(http(s)?:\/\/.)(www\.)?[-a-zA-Z0-9@:%._~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_.~#?&//=]*)/g) ? undefined : 'Must be a valid url'

export const intervalValueLength = (min_length, max_length) => value => !value || (value.length >= min_length && value.length <= max_length) ? undefined : `This field must be of length higger than ${min_length} and smaller than ${max_length} and it is ${value.length}`
