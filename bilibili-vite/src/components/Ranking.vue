<template>
  <div class="container">
    <el-menu class="el-menu-demo" mode="horizontal" style="width: 100%;" :default-active="selectedTab"
      @select="selectTab">
      <el-menu-item @click="navigateToMainpage">
        <img src="/icon/logo.png" class="logo" />
        <span
          style="font-size: 24px;font-family: 'ZCOOL KuaiLe', cursive;color: rgb(0, 178, 255);margin-left: 10px;">热点关注倾向实时分析</span>
      </el-menu-item>
      <div class="flex-grow" style="flex-grow: 1;" />
      <el-menu-item index="ranking">热门内容</el-menu-item>
      <el-sub-menu index="analysis">
        <template #title><b>分析模式</b></template>
        <el-menu-item index="keywords" @click="navigateToWordCloud">关键词分析</el-menu-item>
        <el-menu-item index="videos" @click="navigateToWordCloud">视频分析</el-menu-item>
      </el-sub-menu>
      <!-- <el-menu-item index="settings">设置</el-menu-item> -->
      <el-menu-item index="settings" @click="navigateToSettings">
        设置
      </el-menu-item>
    </el-menu>
    <div class="overlay" v-show="isRefreshing"></div>

    <!-- 次级导航栏 -->
    <el-menu class="secondary-menu" mode="horizontal"
      style="width: 100%;box-shadow: 0 0 6px 2px lightblue; position: relative; top: 48px; justify-content: space-between;"
      v-if="selectedTab === 'ranking'" :default-active="secondarySelected" @select="selectSecondaryTab">
      <el-menu-item index="all" @click="handleSecondaryMenuClick(0)">全站</el-menu-item>
      <el-menu-item index="animation" @click="handleSecondaryMenuClick(1)">动画 <img src="/icon/douga.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="music" @click="handleSecondaryMenuClick(3)">音乐 <img src="/icon/music.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="dance" @click="handleSecondaryMenuClick(129)">舞蹈 <img src="/icon/dance.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="game" @click="handleSecondaryMenuClick(4)">游戏 <img src="/icon/game.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="knowledge" @click="handleSecondaryMenuClick(36)">知识 <img src="/icon/knowledge.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="tech" @click="handleSecondaryMenuClick(188)">科技 <img src="/icon/tech.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="sports" @click="handleSecondaryMenuClick(234)">运动 <img src="/icon/sports.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="car" @click="handleSecondaryMenuClick(223)">汽车 <img src="/icon/car.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="life" @click="handleSecondaryMenuClick(160)">生活 <img src="/icon/life.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="food" @click="handleSecondaryMenuClick(211)">美食 <img src="/icon/food.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="animal" @click="handleSecondaryMenuClick(217)">动物圈 <img src="/icon/animal.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="kichiku" @click="handleSecondaryMenuClick(119)">鬼畜 <img src="/icon/kichiku.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="fashion" @click="handleSecondaryMenuClick(155)">时尚 <img src="/icon/fashion.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="ent" @click="handleSecondaryMenuClick(5)">娱乐 <img src="/icon/ent.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="cinephile" @click="handleSecondaryMenuClick(181)">影视 <img src="/icon/cinephile.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="documentary" @click="handleSecondaryMenuClick(177)">纪录片 <img src="/icon/documentary.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="movie" @click="handleSecondaryMenuClick(23)">电影 <img src="/icon/movie.svg" class="sub-icon" /></el-menu-item>
      <el-menu-item index="tv" @click="handleSecondaryMenuClick(11)">电视剧 <img src="/icon/tv.svg" class="sub-icon" /></el-menu-item>
      <!-- 添加其他分区选项 -->
    </el-menu>
    <!-- 热门内容的元素 -->
    <el-card class="box-card" style="margin-top: 70px;margin-left: 50px;width: 1425px;max-height: 80%;">
      <div class="related-videos">
        <div class="video" style="width: calc(20% - 20px);" v-for="(video, index) in RankingData" :key="index">
          <a :href="`https://www.bilibili.com/video/${video[0]}`" target="_blank">
            <div class="video-cover-container">
              <img :src="`/cover/${video[0]}.jpg`" alt="Video cover" class="video-cover"
                @error="handleImageError(video)">
              <video-icon class="video-icon" />
              <span class="video-views">{{ formatViews(Number(video[17])) }}</span>
              <danmaku-icon class="danmaku-icon" />
              <span class="danmaku-views">{{ formatViews(Number(video[18])) }}</span>
              <span class="video-duration">{{ formatDuration(Number(video[11])) }}</span>
            </div>
            <el-tooltip class="item" effect="dark" placement="bottom">
              <template #content>
                <span v-html="getVideoInfo(video)"></span>
              </template>
              <p class="video-title">{{ video[7] }}</p>
            </el-tooltip>
          </a>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import axios from 'axios';
import { key } from '../store';
import VideoIcon from './video_icon.vue';
import DanmakuIcon from './danmaku_icon.vue'
import VideoSearching from './video_searching.vue';

export default {
  components: {
    'video-icon': VideoIcon,
    'danmaku-icon': DanmakuIcon,
    'video-searching': VideoSearching
  },
  data() {
    return {
      bvid: '',
    };
  },
  methods: {
    navigateToMainpage() {
      this.$router.push({ name: 'MainPage' }); // 使用路由的名称导航到 Mainpage.vue
    },
    navigateToSettings() {
      this.$router.push({ name: 'Settings' }); // 使用路由的名称导航到 Settings.vue
    },
    navigateToWordCloud() {
      this.$router.push({ name: 'WordCloud' }); // 使用路由的名称导航到 WordCloud.vue
    },
    formatViews(views: number) {
      if (views >= 10000) {
        const formattedViews = (views / 10000).toFixed(1);
        if (formattedViews.endsWith('.0')) {
          return parseInt(formattedViews) + '万';
        }
        return formattedViews + '万';
      }
      return views;
    },
    formatDuration(seconds: number) {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      if (hours > 0) {
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
      } else {
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
      }
    },
  },
  setup() {
    const store = useStore(key);
    const keywords = computed(() => store.state.keywords);
    const RankingData = computed(() => store.state.RankingData);
    const wordCloudImage = ref('');
    const selectedKeyword = ref<string | null>(null);
    const keywordDetail = ref<(string | number)[] | null>(null);
    const relatedVideos = ref<(string | number)[][] | null>(null);
    const isRefreshing = ref(false);
    const selectedTab = ref(localStorage.getItem('selectedTab') || 'keywords');
    const secondarySelected = ref(localStorage.getItem('secondarySelected') || 'all');

    const selectTab = (tab: string) => {
      // if (tab === 'keywords' || tab === 'videos' || tab === 'settings' || tab === 'ranking') {
      if (tab === 'keywords' || tab === 'videos' || tab === 'settings' || tab === 'ranking') {
        selectedTab.value = tab;
        localStorage.setItem('selectedTab', tab);
      }
    };

    const selectSecondaryTab = (tab: string) => {
      secondarySelected.value = tab;
      localStorage.setItem('secondarySelected', tab);
    };

    // 当页面加载时，检查 localStorage 中是否有用户的选择
    onMounted(() => {
      const storedTab = localStorage.getItem('selectedTab');
      if (storedTab) {
        selectedTab.value = storedTab;
      }
      const storedSecondaryTab = localStorage.getItem('secondarySelected'); // 添加此行
      if (storedSecondaryTab) { // 添加此行
        secondarySelected.value = storedSecondaryTab; // 添加此行
      } // 添加此行
    });

    const handleRowClick = (row: (string | number)[]) => {
      selectedKeyword.value = row[0] as string;
    };

    const closeDetail = () => { // 添加这个函数
      keywordDetail.value = null;
    };

    const handleImageError = (video: (string | number)[]) => {
      console.error(`Failed to load image for video: ${video[0]}`);
    };

    const getVideoInfo = (video: (string | number)[]) => {
      return `
        视频标题：${video[7]}<br>
        视频简介：<pre>${video[10]}</pre><br>
        视频标签：${video[13]}<br>
        分类：${video[4]}<br>
        bv号：${video[0]}<br>
        av号：${video[1]}
      `;
    };

    const handleSecondaryMenuClick = (tid: number) => {
      // 向后端发送请求
      axios.get(`http://localhost:5000/api/ranking?tid=${tid}`)
        .then(response => {
          // 更新 store 中的 RankingData
          store.commit('setRankingData', response.data);
          // console.log(response.data);
        })
        .catch(error => {
          console.error('Error fetching ranking data:', error);
        });
    };


    return {
      selectedTab,
      selectTab,
      keywords,
      RankingData,
      isRefreshing,
      selectedKeyword,
      wordCloudImage,
      handleRowClick,
      keywordDetail,
      closeDetail,
      relatedVideos,
      handleImageError,
      getVideoInfo,
      handleSecondaryMenuClick,
      secondarySelected, // 添加此行
      selectSecondaryTab, // 添加此行
    };
  }
}
</script>

<style scoped>
.keyword-section {
  display: flex;
  flex-direction: row;
}

.el-menu-vertical-demo {
  border-right: 1px solid #ddd;
  position: fixed;
  height: 100%;
  width: 150px;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0);
  z-index: 9999;
}

pre {
  white-space: pre-line;
  font-family: Arial;
}

.container {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0px;
  left: 0px;
  background-image: url('/icon/wordcloud.png');
  background-size: contain;
  background-repeat: repeat;
  display: flex;
  /* 修改这行 */
  flex-direction: column;
  /* 添加这行 */
}

.box-card {
  /* width: 30%; */
  box-shadow: 0 0 6px 2px lightblue !important;
  background-color: rgba(255, 255, 255, 0.85);
}

.related-videos {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  max-height: 500px;
  /* 修改这里为你想要的高度 */
  overflow-y: auto;
  /* 添加这行 */
}

.video {
  width: calc(33% - 20px);
  /* 修改这里 */
  aspect-ratio: 16 / 9;
  margin-bottom: 20px;
  margin-right: 20px;
}

.video-icon {
  position: absolute;
  bottom: -2px;
  left: 0;
  z-index: 2;
}

.video-views {
  position: absolute;
  bottom: 7.5px;
  left: 24px;
  margin-right: 2px;
  color: #fff;
  font-family: 'PingFang SC';
  font-size: 12px;
  z-index: 2;
}

.danmaku-icon {
  position: absolute;
  bottom: -2px;
  left: 70px;
  z-index: 2;
}

.danmaku-views {
  position: absolute;
  bottom: 7.5px;
  left: 93px;
  margin-right: 2px;
  color: #fff;
  font-family: 'PingFang SC';
  font-size: 12px;
  z-index: 2;
}

.video-duration {
  position: absolute;
  bottom: 8px;
  right: 5px;
  color: #fff;
  font-family: 'PingFang SC';
  font-size: 12px;
  z-index: 2;
}

.video-cover {
  width: 100%;
  border-radius: 10px;
}

.video-cover-container {
  position: relative;
}

.video-cover-container::after {
  content: "";
  position: absolute;
  bottom: 5px;
  left: 0;
  width: 100%;
  height: 30%;
  /* 可根据需要调整遮罩的高度 */
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
  z-index: 1;
  border-radius: 10px;
}

.video-title {
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  font-size: 15px;
  font-family: PingFang SC;
  font-weight: bold;
}

.video a {
  color: black;
  text-decoration: none;
}

.video a:hover {
  color: rgb(0, 174, 236);
}

.el-menu-item {
  text-align: center;
  /* font-family: 'Anta', sans-serif; */
  font-weight: bold;
}

.el-menu-demo {
  background: linear-gradient(to right, rgb(255, 255, 255), rgb(168, 158, 255));
  position: fixed;
  width: 100%;
  z-index: 1000;
  /* 确保顶部栏在其他元素之上 */
}

.logo {
  height: 30px;
  /* 调整为适合的大小 */
  width: auto;
}

.secondary-menu {
  background: linear-gradient(to right, rgb(255, 255, 255), rgb(210, 158, 255));
  margin-top: 10px;
}

.sub-icon {
  width: 20px;
  height: 20px;
  margin-left: 5px;
}
</style>