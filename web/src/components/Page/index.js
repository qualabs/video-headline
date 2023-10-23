import React, {Component} from 'react'
import {connect} from 'react-redux'
import ResponsiveMenu from 'react-responsive-navbar'

import FlashMessage from '../FlashMessage'
import {hideShowMenu} from '../../actions/utils'

import './index.css'


class Page extends Component {
  constructor () {
    super()
    this.menuHandler = this.menuHandler.bind(this)
  }

  menuHandler (e) {
    e.preventDefault()
    this.props.hideShowMenu()
  }

  renderMenu () {
    const {menuItems} = this.props
    const items = menuItems.map((item, index) => {
      return <li key={index}>{item}</li>
    })
    return (
      <div className='container-fluid'>
        <ul>
          {items}
        </ul>
      </div>
    )
  }

  render () {
    const {header, menuItems} = this.props

    return (
      <div className='page'>

        {header ? (
          <div className='page-header'>
            <div className='container-fluid'>
              <button className='btn btn-primary menu-button' onClick={e => this.menuHandler(e)}>
                <i className='fas fa-bars fa-2x'></i>
              </button>
              {header}
            </div>
          </div>
        ) : null}

        {menuItems &&
          <ResponsiveMenu
            changeMenuOn='500px'
            largeMenuClassName='navbar-menu'
            smallMenuClassName='navbar-menu'
            menuOpenButton={<div className='btn'><i className='fas fa-bars'></i> Options</div>}
            menuCloseButton={<div className='btn'><i className='fas fa-times'></i> Close</div>}
            menu={this.renderMenu()}
          />}

        <FlashMessage />
        <div className='content'>
          {this.props.children}
        </div>
      </div>
    )
  }
}

function mapStateToProps ({show_sidebar}) {
  return {show_sidebar}
}

export default connect(mapStateToProps, {hideShowMenu})(Page)
