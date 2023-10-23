import React from 'react'
import {Tooltip as BoostrapTooltip, OverlayTrigger} from 'react-bootstrap'

class Tooltip extends React.Component {
  render () {
    const {text, placement, show} = this.props

    if (!show) {
      return <>{this.props.children}</>
    }

    return (
      <OverlayTrigger
        key={placement}
        placement={placement}
        overlay={<BoostrapTooltip id={`tooltip-${placement}`} style={{opacity: '1'}} className='in'>{text}</BoostrapTooltip>}
      >
        <div className='tooltip-target'>
          {this.props.children}
        </div>
      </OverlayTrigger>
    )
  }
}

export default Tooltip
