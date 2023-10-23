import React, {Component} from 'react'
import {Switch, Route} from 'react-router-dom'
import LoginPage from './LoginPage'

import {connect} from 'react-redux'
import {withRouter} from 'react-router'

import history from '../../history'


class AnnonymousRoutes extends Component {
  render () {
    return (
      <Switch>
        <Route exact path='/' component={LoginPage}/>
        <Route path='*' render={() => <div>{history.push('/')}</div>} />
      </Switch>
    )
  }
}

export default withRouter(connect()(AnnonymousRoutes))
