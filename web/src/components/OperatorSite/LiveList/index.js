import React, {Component} from 'react'
import {connect} from 'react-redux'
import {fetchLiveVideos, clearLiveVideo} from '../../../actions/live'
import {fetchTag} from '../../../actions/tags'
import {DragDropContext, Droppable, Draggable} from 'react-beautiful-dnd'

import './index.css'


class LiveList extends Component {

  getItems (count, offset = 0) {
    return (
      Array.from({length: count}, (v, k) => k).map((k) => ({
        id: `item-${k + offset}-${new Date().getTime()}`,
        content: `item ${k + offset}`
      }))
    )
  }

  constructor (props) {
    super()
    this.state = [this.getItems(10), this.getItems(5, 10)]
  }

  componentDidMount () {
    console.log ("I'm gettnng started!!")
  }


  reorder (list, startIndex, endIndex) {
    const result = Array.from(list)
    const [removed] = result.splice(startIndex, 1)
    result.splice(endIndex, 0, removed)
    console.log('reordenando')
    return result
  }

  /**
 * Moves an item from one list to another list.
 */
  move (source, destination, droppableSource, droppableDestination) {
    const sourceClone = Array.from(source)
    const destClone = Array.from(destination)
    const [removed] = sourceClone.splice(droppableSource.index, 1)
    console.log('moviendo')

    destClone.splice(droppableDestination.index, 0, removed)

    const result = {}
    result[droppableSource.droppableId] = sourceClone
    result[droppableDestination.droppableId] = destClone

    return result
  }


  getListStyle (isDraggingOver) {
    return ({
      background: isDraggingOver ? 'lightblue' : 'lightgrey',
      padding: 8,
      width: 250
    })
  }

  onDragEnd (result) {
    const {source, destination} = result

    // dropped outside the list
    if (!destination) {
      return
    }
    const sInd = +source.droppableId
    const dInd = +destination.droppableId

    if (sInd === dInd) {
      const items = this.reorder(this.state[sInd], source.index, destination.index)
      const newState = [...this.state]
      newState[sInd] = items
      this.setState(newState)
    } else {
      const result = this.move(this.state[sInd], this.state[dInd], source, destination)
      const newState = [...this.state]
      newState[sInd] = result[sInd]
      newState[dInd] = result[dInd]

      this.setState(newState.filter((group) => group.length))
    }
  }


  render () {
    return (
      <div>
        <button
          type='button'
          onClick={() => {
            this.setState([...this.state, []])
          }}
        >
        Add new group
        </button>
        <button
          type='button'
          onClick={() => {
            this.setState([...this.state, this.getItems(1)])
          }}
        >
        Add new item
        </button>
        <div style={{display: 'flex'}}>
          <DragDropContext onDragEnd={this.onDragEnd}>
            {this.state.map((el, ind) => (
              <Droppable key={ind} droppableId={`${ind}`}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    style={this.setListStyle(snapshot.isDraggingOver)}
                    {...provided.droppableProps}
                  >
                    {el.map((item, index) => (
                      <Draggable
                        key={item.id}
                        draggableId={item.id}
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            style={this.getItemStyle(
                              snapshot.isDragging,
                              provided.draggableProps.style
                            )}
                          >
                            <div
                              style={{
                                display: 'flex',
                                justifyContent: 'space-around'
                              }}
                            >
                              {item.content}
                              <button
                                type='button'
                                onClick={() => {
                                  const newState = [...this.state]
                                  newState[ind].splice(index, 1)
                                  this.setState(
                                    newState.filter((group) => group.length)
                                  )
                                }}
                              >
                              delete
                              </button>
                            </div>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            ))}
          </DragDropContext>
        </div>
      </div>
    )
  }
}

function mapStateToProps ({list, session, tag}) {
  return {
    contents: list.liveVideos,
    user: session.user,
    tag: tag,
  }
}

export default connect(mapStateToProps, {
  fetchLiveVideos,
  clearLiveVideo,
  fetchTag,
})(LiveList)
