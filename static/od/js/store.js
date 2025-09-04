// store.js
const { createStore } = Redux;

// --- Initial state ---
const initialState = {
  selected: [],      // array of selected PKs
  action: null,      // currently selected action
  allSelected: false // true if all items are selected
};

// --- Actions types ---
const SET_SELECTED = 'SET_SELECTED';
const SET_ACTION = 'SET_ACTION';
const TOGGLE_SELECT = 'TOGGLE_SELECT';
const SELECT_ALL = 'SELECT_ALL';
const CLEAR_SELECTION = 'CLEAR_SELECTION';

// --- Reducer ---
function selectionReducer(state = initialState, action) {
  switch (action.type) {
    case SET_SELECTED:
      return { ...state, selected: action.payload, allSelected: false };

    case TOGGLE_SELECT: {
      const pk = action.payload;
      const selected = state.selected.includes(pk)
        ? state.selected.filter(id => id !== pk)
        : [...state.selected, pk];
      return { ...state, selected, allSelected: false };
    }

    case SELECT_ALL:
      return { ...state, allSelected: true, selected: action.payload || [] };

    case CLEAR_SELECTION:
      return { ...state, selected: [], allSelected: false };

    case SET_ACTION:
      return { ...state, action: action.payload };

    default:
      return state;
  }
}

// --- Create store ---
const store = createStore(
  selectionReducer,
  window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__()
);

// --- Action creators ---
const actions = {
  setSelected: selected => store.dispatch({ type: SET_SELECTED, payload: selected }),
  toggleSelect: pk => store.dispatch({ type: TOGGLE_SELECT, payload: pk }),
  selectAll: allPks => store.dispatch({ type: SELECT_ALL, payload: allPks }),
  clearSelection: () => store.dispatch({ type: CLEAR_SELECTION }),
  setAction: actionName => store.dispatch({ type: SET_ACTION, payload: actionName })
};

export { store, actions };
