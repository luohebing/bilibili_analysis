// router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import MainPage from '../src/components/MainPage.vue'; // 导入主页面组件
import WordCloud from '../src/components/WordCloud.vue'; // 导入词云展示页面组件
import Settings from '../src/components/Settings.vue'; //导入设置组件

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
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
