import React, {Component} from 'react'
import './index.css'
import Dragula from 'react-dragula'

class DraggableArea extends Component {
  dragulaDecorator = (componentBackingInstance) => {
    if (componentBackingInstance) {
      let options = {
        revertOnSpill: true
      }

      Dragula(
        [
          document.getElementById('assets'),
          document.getElementById('loop_order')
        ],
        options
      ).on('drop', () => console.log('Item dropped'))
    }
  };

  render () {
    const assets = [
      {title: 'Ad Available', info: 'Variable Length'},
      {title: 'Ad Available 2', info: 'Variable Length 2'}
    ]

    const loopOrder = [{title: 'Qualabs Intro', info: '1 Hour'}]

    return (
      <div className='container'>
        <div id='assets' className='assets' ref={this.dragulaDecorator}>
          {assets.map((item) => (
            <DraggableItem key={item.title} {...item} />
          ))}
        </div>
        <div id='loop_order' className='loop_order' ref={this.dragulaDecorator}>
          {loopOrder.map((item) => (
            <DraggableItem key={item.title} {...item} />
          ))}
        </div>
      </div>
    )
  }
}

const DraggableItem = ({title, info}) => (
  <div className='draggable-item'>
    <div>
      <div className='item-title'>{title}</div>
      <div className='item-info'>{info}</div>
    </div>
  </div>
)

export default DraggableArea
