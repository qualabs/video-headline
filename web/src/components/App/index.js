import React, {Component} from 'react'
import {withRouter} from 'react-router-dom'
import {connect} from 'react-redux'

import {resumeSession} from '../../actions/user'

import {OperatorRoutes} from '../OperatorSite/navigation'
import AnnonymousRoutes from '../AnonymousSite/navigation'

import Menu from '../Menu'
import Loading from '../Loading'

import '../../styles/fonts/Font-Awesome-Pro/css/fontawesome.css'
import '../../styles/fonts/Font-Awesome-Pro/css/fa-solid.css'
import './app.css'
import 'bootstrap/dist/css/bootstrap.min.css'

class App extends Component {
  componentDidMount () {
    this.props.resumeSession()
  }

  renderRoutes () {
    const {user} = this.props.session
    return <OperatorRoutes user={user} />
  }

  render () {
    const {session} = this.props
    if (!session.appInitialized) {
      return <Loading fullscreen={true} />
    }
    if (!session.user) {
      return <AnnonymousRoutes />
    }

    return (
      <Menu>
        {this.renderRoutes()}
      </Menu>
    )
  }
}

function mapStateToProps ({session}) {
  return {session}
}

export default withRouter(connect(mapStateToProps, {resumeSession})(App))
