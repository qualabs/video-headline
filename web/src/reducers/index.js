import {combineReducers} from 'redux'
import {reducer as formReducer} from 'redux-form'
import sessionReducer from './sessionReducer'
import listReducer from './listReducer'
import videoReducer from './videoReducer'
import liveReducer from './liveReducer'
import channelReducer from './channelReducer'
import cutReducer from './cutReducer'

import dashboardReducer from './dashboardReducer'
import billsReducer from './billsReducer'
import subBillReducer from './subBillReducer'

import flashMessageReducer from './flashMessageReducer'

import menuReducer from './menuReducer'
import trackingReducer from './trackingReducer'
import tagReducer from './tagReducer'
import monitorReducer from './monitorReducer'
import securityReducer from './securityReducer'

export default combineReducers({
  form: formReducer,
  session: sessionReducer,
  dashboardPage: dashboardReducer,
  bill: billsReducer,
  subBill: subBillReducer,
  list: listReducer,
  flashMessage: flashMessageReducer,
  show_menu: menuReducer,
  channel: channelReducer,
  video: videoReducer,
  live: liveReducer,
  cut: cutReducer,
  tracking: trackingReducer,
  monitor: monitorReducer,
  tag: tagReducer,
  security: securityReducer
})
