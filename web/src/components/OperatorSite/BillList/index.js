import React, {Component} from 'react'
import {connect} from 'react-redux'

import Page from '../../Page'

import BillTable from '../Table/BillTable'
import {fetchBills} from '../../../actions/bill'

class BillList extends Component {
  render () {
    return (
      <Page header={<h1> Usage Report </h1>}>
        <div className='container-fluid'>
          <BillTable
            list={this.props.contents}
            fetch={this.props.fetchBills.bind(this)}
          />
        </div>
      </Page>
    )
  }
}

function mapStateToProps ({list, session}) {
  return {
    contents: list.bills,
    user: session.user,
  }
}

export default connect(mapStateToProps, {fetchBills})(BillList)
