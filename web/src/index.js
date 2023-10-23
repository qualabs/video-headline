import React from 'react'
import ReactDOM from 'react-dom'

import {createStore, applyMiddleware, compose} from 'redux'
import {Provider} from 'react-redux'
import {connectRouter, routerMiddleware, ConnectedRouter} from 'connected-react-router'
import rootReducer from './reducers'
import thunk from 'redux-thunk'
import history from './history'
import App from './components/App'


const initialState = {}


let composeEnhancers = compose
if (process.env.NODE_ENV === 'development') {
  composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose
}

const store = createStore(
  connectRouter(history)(rootReducer), // new root reducer with router state
  initialState,
  composeEnhancers(
    applyMiddleware(
      routerMiddleware(history), // for dispatching history actions
      thunk
    ),
  ),
)

ReactDOM.render(
  <Provider store={store}>
    <ConnectedRouter history={history}>
      <App />
    </ConnectedRouter>
  </Provider>,
  document.getElementById('root'))
