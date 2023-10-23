import React, {Component} from 'react'

import Page from '../../Page'
import Form from '../ChannelForm'


export default class ChannelNew extends Component {
  render () {
    return (
      <Page header={<h1>New Video Group</h1>}>
        <div className='container-fluid subscriber-new'>
          <Form />
        </div>
      </Page>
    )
  }
}
