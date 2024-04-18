// router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import MainPage from '../src/components/MainPage.vue'; // 导入主页面组件
import WordCloud from '../src/components/WordCloud.vue'; // 导入词云展示页面组件
import Settings from '../src/components/Settings.vue'; //导入设置组件
import Ranking from '../src/components/Ranking.vue'; //导入热门组件

const routes = [
  {
    path: '/',
    name: 'MainPage',
    component: MainPage
  },
  {
    path: '/wordcloud',
    name: 'WordCloud',
    component: WordCloud
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/ranking',
    name: 'Ranking',
    component: Ranking
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
