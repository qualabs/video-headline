import React, {Component} from 'react'

import Page from '../../Page'
import Form from '../LiveForm'


export default class LiveNew extends Component {
  render () {
    return (
      <Page header={<h1>New Live Video</h1>}>
        <div className='container-fluid subscriber-new'>
          <Form />
        </div>
      </Page>
    )
  }
}
