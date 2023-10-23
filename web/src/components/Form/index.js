import React, {Component} from 'react'
import Multiselect from 'react-widgets/lib/Multiselect'
import DropDownList from 'react-widgets/lib/DropdownList'
import DateTimePicker from 'react-widgets/lib/DateTimePicker'
import momentLocalizer from 'react-widgets-moment'
import moment from 'moment'
import Toggle from 'react-toggle'
import classnames from 'classnames'

import {Editor} from 'react-draft-wysiwyg'
import '../../../node_modules/react-draft-wysiwyg/dist/react-draft-wysiwyg.css'
import {convertToRaw, convertFromRaw, EditorState} from 'draft-js'
import {mdToDraftjs, draftjsToMd} from 'draftjs-md-converter'
import keys from 'lodash/keys'


import 'react-widgets/dist/css/react-widgets.css'
import 'react-toggle/style.css'
import './form.css'
import './index.css'
import 'moment/locale/en-gb'


moment.locale('en-gb')
momentLocalizer()


export class FormGroup extends Component {
  render () {
    const {labelText, helpText} = this.props
    const label = labelText && (
      <label htmlFor={this.props.children.props.name}>
        {labelText}
      </label>
    )
    const help = helpText && <small>{helpText}</small>
    return (
      <div className={classnames('form-group', this.props.className || '')}>
        {label}
        {this.props.children}
        {help}
      </div>
    )
  }
}

class FormFieldError extends Component {
  render () {
    const {meta} = this.props
    const hasError = meta.touched && meta.error
    const hasWarning = meta.warning
    return (
      <div className={classnames({'invalid': hasError})}>
        {this.props.children}
        {hasError && (
          <div className='text-danger'>
            <small><i className='fas fa-times'/> {meta.error}</small>
          </div>
        )}
        {hasWarning && (
          <div className='warning'>
            <i className='fas fa-exclamation-circle'/> {meta.warning}
          </div>
        )}
      </div>
    )
  }
}

export class InputField extends Component {
  render () {
    const {meta} = this.props
    const hasError = meta.touched && meta.error
    return (
      <FormFieldError {...this.props}>
        <input {...this.props.input}
          disabled={this.props.disabled}
          type={this.props.type || 'text'}
          id={this.props.input.name}
          className={classnames(this.props.className || 'form-control', {'is-invalid': hasError})}
        />
      </FormFieldError>
    )
  }
}

export class CheckboxField extends Component {
  render () {
    return (
      <FormFieldError {...this.props}>
        <Toggle name={this.props.input.name}
          checked={this.props.input.value ? true : false}
          onChange={this.props.input.onChange}
          {...this.props}
          className={this.props.className || 'form-check-input'}
        />
      </FormFieldError>
    )
  }
}

export class SelectField extends Component {
  render () {
    return (
      <FormFieldError {...this.props}>
        <select {...this.props.input}
          id={this.props.input.name}>
          {this.props.children}
          className={this.props.className || 'form-control'}
        </select>
      </FormFieldError>
    )
  }
}

export class MultiselectField extends Component {
  handleCreate (name) {
    if (this.props.allowCreate) {
      const newOption = {
        id: null,
        name
      }

      const {input} = this.props
      input.onChange([...input.value, newOption])
    }
  }

  render () {
    const {input, data, disabled, filter, valueField, textField, onSearch,
      allowCreate} = this.props
    return (
      <FormFieldError {...this.props}>
        <Multiselect {...input}
          onBlur={() => input.onBlur()}
          value={input.value || []} // requires value to be an array
          data={data}
          disabled={disabled}
          filter={filter}
          valueField={valueField}
          textField={textField}
          onSearch={onSearch}
          allowCreate={allowCreate || false}
          onCreate={name => this.handleCreate(name)}
          className={this.props.className}
        />
      </FormFieldError>
    )
  }
}

export class ObjectMultiselectField extends Component {
  constructor () {
    super()
    this.options = []
  }

  updateAvailableOptions () {
    const {data, valueField, textField} = this.props

    this.options = data.reduce((result, obj) => {
      result[obj[valueField]] = obj[textField]
      return result
    }, {})
  }

  handleCreate (name) {
    if (this.props.allowCreate) {

      const {input} = this.props
      input.onChange([...input.value, name])
    }
  }

  render () {
    const {input, disabled, filter, allowCreate, onSearch, className} = this.props

    this.updateAvailableOptions()

    return (
      <FormFieldError {...this.props}>
        <Multiselect {...input}
          onBlur={() => input.onBlur()}
          data={keys(this.options)}
          value={input.value || []}
          disabled={disabled}
          filter={filter}
          textField={val => val && (this.options[val] || val)}
          onSearch={onSearch}
          allowCreate={allowCreate || false}
          onCreate={(name) => this.handleCreate(name)}
          className={className}
        />
      </FormFieldError>
    )
  }
}

const messagesLocalized = {
  emptyList: 'No options found',
  emptyFilter: 'No results found',
  filterPlaceholder: 'Search...'
}

export class DropDownListField extends Component {
  render () {
    const {input, data, disabled, filter, allowCreate, onCreate, valueField,
      textField, onSearch} = this.props
    return (
      <FormFieldError {...this.props}>
        <DropDownList {...input}
          onBlur={() => input.onBlur()}
          data={data}
          disabled={disabled}
          filter={filter}
          allowCreate={allowCreate}
          onCreate={onCreate}
          valueField={valueField}
          textField={textField}
          messages={messagesLocalized}
          onSearch={onSearch} />
      </FormFieldError>
    )
  }
}

export class ObjectDropDownListField extends Component {
  render () {
    const {input, data, disabled, filter, allowCreate, onCreate, valueField,
      textField, onSearch} = this.props

    const options = data.reduce((result, obj) => {
      result[obj[valueField]] = obj[textField]
      return result
    }, {})

    return (
      <FormFieldError {...this.props}>
        <DropDownList {...input}
          onBlur={() => input.onBlur()}
          data={keys(options)}
          disabled={disabled}
          filter={filter}
          allowCreate={allowCreate}
          onCreate={onCreate}
          textField={val => val && options[val]}
          messages={messagesLocalized}
          onSearch={onSearch} />
      </FormFieldError>
    )
  }
}


export class DateTimePickerField extends Component {
  render () {
    const {input: {onChange, value}, showTime, disabled} = this.props
    return (
      <FormFieldError {...this.props}>
        <DateTimePicker
          onChange={onChange}
          format='LLL'
          time={showTime}
          disabled={disabled}
          // requires value to be an array
          value={!value ? null : new Date(value)} />
      </FormFieldError>
    )
  }
}

export class MarkdownFieldEditor extends Component {
  constructor (props) {
    super(props)
    this.state = {
      editorState: EditorState.createWithContent(convertFromRaw(mdToDraftjs(props.input.value)))
    }
  }

  onEditorStateChange (editorState) {
    const {input: {onChange}} = this.props
    this.setState({editorState})
    onChange(draftjsToMd(convertToRaw(editorState.getCurrentContent())))
  }

  render () {
    return (
      <Editor
        name='description'
        editorClassName='markdown-editor'
        editorState= {this.state.editorState}
        onEditorStateChange={this.onEditorStateChange.bind(this)}
        toolbar={{
          options: ['inline', 'blockType', 'list', 'link', 'remove', 'history'],
        }}
      />
    )
  }
}
