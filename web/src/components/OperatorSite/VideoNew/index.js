import React, {Component} from 'react'

import Form from '../VideoForm'
import Page from '../../Page'

export default class VideoNew extends Component {
  render () {
    return (
      <Page header={<h1>New Video</h1>}>
        <div className='container-fluid'>
          <Form />
        </div>
      </Page>
    )
  }
}
