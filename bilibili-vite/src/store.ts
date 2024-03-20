// store.ts
import { InjectionKey } from 'vue';
import { createStore, Store } from 'vuex';
import createPersistedState from 'vuex-persistedstate';

export interface State {
    keywords: any[];
    RankingData: any[];
}

export const key: InjectionKey<Store<State>> = Symbol();

export const store = createStore<State>({
  plugins: [createPersistedState()],
  state: {
    keywords: [],
    RankingData: [],
  },
  mutations: {
    setKeywords(state, keywords: any[]) {
      state.keywords = keywords;
    },
    setRankingData(state, RankingData: any[]) {
      state.RankingData = RankingData;
    },
  },
});