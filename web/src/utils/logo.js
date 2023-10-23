import React from 'react'
import {Link} from 'react-router-dom'

import logo from '../images/qualabs_logo.png'

export function getLogoWithLink () {
  return (
    <Link to='/'>
      <img src={logo} alt='Qualabs' />
    </Link>
  )
}

export function getLogo () {
  return (
    <img src={logo} alt='Qualabs' className='flex-item'/>
  )
}
