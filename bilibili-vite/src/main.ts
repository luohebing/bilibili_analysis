import { createApp } from 'vue';
import { store, key } from './store';
import './style.css';
import App from './App.vue';
import router from '../router'; // 导入路由实例
import ElementPlus from 'element-plus';
import 'element-plus/theme-chalk/index.css';
import locale from 'element-plus/es/locale/lang/zh-cn'


// createApp(App).mount('#app')
createApp(App).use(store, key).use(router).use(ElementPlus, { locale }).mount('#app');
