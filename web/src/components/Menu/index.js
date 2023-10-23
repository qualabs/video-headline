import React, {Component} from 'react'
import {connect} from 'react-redux'
import Sidebar from 'react-sidebar'

import {logout} from '../../actions/user'
import {hideShowMenu} from '../../actions/utils'

import OperatorMenu from '../OperatorSite/navigation'

import {getLogoWithLink} from '../../utils/logo'
import './menu.css'


// This const is used by some components that need to find this part
// of the page (scroll things...)
const MENU_CONTENT_CLASS_NAME = 'menu-content'
const mql = window.matchMedia(`(min-width: 800px)`)

export function getMenuContentEl () {
  // Returns the Content's Element (node)
  return document.getElementsByClassName(MENU_CONTENT_CLASS_NAME)[0]
}

class Menu extends Component {
  constructor () {
    super()
    this.logoutHandler = this.logoutHandler.bind(this)
    this.state = {
      sidebarDocked: mql.matches,
      sidebarOpen: this.show_menu
    }

    this.mediaQueryChanged = this.mediaQueryChanged.bind(this)
    this.onSetSidebarOpen = this.onSetSidebarOpen.bind(this)
  }

  componentWillMount () {
    mql.addListener(this.mediaQueryChanged)
  }

  componentWillUnmount () {
    mql.removeListener(this.mediaQueryChanged)
  }

  onSetSidebarOpen () {
    this.props.hideShowMenu()
  }

  mediaQueryChanged () {
    this.setState({sidebarDocked: mql.matches, sidebarOpen: false})
  }

  logoutHandler (e) {
    e.preventDefault()
    this.props.logout()
  }

  renderMenuLinks () {
    const {user} = this.props.session
    return <OperatorMenu user={user} />
  }

  renderUser () {
    const {user} = this.props.session
    return [
      <li key='username' className='user'>
        <div><i className='fas fa-fw fa-user'></i> <b>{user.username}</b></div>
      </li>,
      <li key='org' className='user'>
        <div><i className='fas fa-fw fa-building'></i> <b>{user.organization.name}</b></div>
      </li>
    ]
  }

  renderMenu () {
    return (
      <div className='menu'>
        <div className='menu-header'>
          {getLogoWithLink()}
        </div>
        <div className='menu-links'>
          <ul>
            {this.renderMenuLinks()}
            <hr/>
            {this.renderUser()}
            <li><a className='btn' onClick={e => this.logoutHandler(e)} href='/'><i className='fas fa-fw fa-sign-out'/>Logout</a></li>
          </ul>
        </div>
      </div>
    )
  }

  render () {
    const {show_menu} = this.props
    return (
      <Sidebar
        rootClassName	='menu'
        sidebarClassName='menu-sidebar'
        contentClassName={MENU_CONTENT_CLASS_NAME}
        overlayClassName='menu-overlay'
        sidebar={this.renderMenu()}
        transitions={false}
        touch={true}
        touchHandleWidth={15}
        shadow={true}
        docked={this.state.sidebarDocked}
        open= {show_menu}
        onSetOpen={this.onSetSidebarOpen}
      >
        {this.props.children}
      </Sidebar>
    )
  }
}

function mapStateToProps ({session, show_menu}) {
  return {
    session: session,
    show_menu: show_menu.show_menu
  }
}

export default connect(mapStateToProps, {logout, hideShowMenu})(Menu)
