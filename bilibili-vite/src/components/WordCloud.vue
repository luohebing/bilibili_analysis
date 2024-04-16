<template>
  <div class="container">
    <el-menu class="el-menu-demo" mode="horizontal" style="width: 100%;box-shadow: 0 0 6px 2px lightblue;"
      :default-active="selectedTab" @select="selectTab">
      <el-menu-item @click="navigateToMainpage">
        <img src="/icon/logo.png" class="logo" />
        <span
          style="font-size: 24px;font-family: 'ZCOOL KuaiLe', cursive;color: rgb(0, 178, 255);margin-left: 10px;">热点关注倾向实时分析</span>
      </el-menu-item>
      <div class="flex-grow" style="flex-grow: 1;" />
      <el-menu-item index="ranking">热门内容</el-menu-item>
      <el-sub-menu index="analysis">
        <template #title><b>分析模式</b></template>
        <el-menu-item index="keywords">关键词分析</el-menu-item>
        <el-menu-item index="videos">视频分析</el-menu-item>
      </el-sub-menu>
      <!-- <el-menu-item index="settings">设置</el-menu-item> -->
      <el-menu-item index="settings" @click="navigateToSettings">
        设置
      </el-menu-item>
    </el-menu>
    <div class="overlay" v-show="isRefreshing"></div>
    <div v-if="selectedTab === 'keywords'" class="keyword-section">
      <!-- 关键词分析的元素 -->
      <el-card class="box-card" style="margin-top: 100px;margin-left: 50px;width: 460px; max-height: 80%;">
        <div slot="header" class="clearfix">
          <span><b>排行榜热搜关键词</b></span>
        </div>
        <el-table :data="keywords" style="width: 100%; overflow-y: auto; max-height: 440px;"
          @row-click="handleRowClick">
          <el-table-column prop="0" label="关键词"></el-table-column>
          <el-table-column prop="1" label="权重">
            <template #default="{ row }">
              <span>{{ row[1].toFixed(3) }}</span>
            </template>
          </el-table-column>
        </el-table>
        <br>
        <el-autocomplete v-model="selectedKeyword" :fetch-suggestions="querySearch" placeholder="请输入关键词"
          @select="handleSelect" trigger-on-focus>
          <template #default="{ item }">
            <div>{{ item.value }} (权重: {{ item.weight.toFixed(3) }})</div>
          </template>
        </el-autocomplete>
        <el-button type="primary" @click="refreshKeywords" v-loading="isRefreshing">刷新关键词</el-button>
        <el-button type="primary" @click="analyzeKeyword">关键词解析</el-button>
      </el-card>
      <el-card v-if="keywordDetail" class="box-card"
        style="margin-top: 100px;margin-left: 100px;width: 825px;max-height: 80%;">
        <div slot="header" class="clearfix">
          <!-- <span><b>关键词详情</b></span> -->
          <el-button type="primary" style="float: right;" @click="closeDetail">关闭</el-button>
          <el-button type="primary" style="float: right; margin-right: 10px;" @click="analyzeSentiment"
            v-loading="isRefreshing">用户情感分析</el-button>
        </div>
        <p><b>关键词</b>：{{ keywordDetail[0] }} <b>权重</b>：{{ (keywordDetail[1] as number).toFixed(3) }}</p>
        <p>相关视频：</p>
        <div class="related-videos">
          <div class="video" v-for="(video, index) in relatedVideos" :key="index">
            <a :href="`https://www.bilibili.com/video/${video[0]}`" target="_blank">
              <div class="video-cover-container">
                <img :src="`/cover/${video[0]}.jpg`" alt="Video cover" class="video-cover"
                  @error="handleImageError(video)">
                <video-icon class="video-icon" />
                <span class="video-views">{{ formatViews(Number(video[17])) }}</span> <!-- 新增的播放量显示 -->
                <danmaku-icon class="danmaku-icon" />
                <span class="danmaku-views">{{ formatViews(Number(video[18])) }}</span>
                <span class="video-duration">{{ formatDuration(Number(video[11])) }}</span> <!-- 新增的视频时长显示 -->
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

    <div v-if="selectedTab === 'videos'">
      <!-- 视频分析的元素 -->
      <video-searching />
    </div>

    <div v-if="selectedTab === 'ranking'">
      <!-- 热门内容的元素 -->
      <el-card class="box-card" style="margin-top: 100px;margin-left: 50px;width: 1425px;max-height: 80%;">
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

    <div v-if="selectedTab === 'settings'">
      <!-- 设置相关的元素 -->
    </div>

  </div>
</template>

<script lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useStore } from 'vuex';
import axios from 'axios';
import { key } from '../store';
import { ElMessage } from 'element-plus';
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
    searchVideo() {
      // 在这里发送请求到后端，获取并显示视频信息
      // 例如：this.$http.get(`/api/videos/${this.bvid}`)
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

    const selectTab = (tab: string) => {
      // if (tab === 'keywords' || tab === 'videos' || tab === 'settings' || tab === 'ranking') {
      if (tab === 'keywords' || tab === 'videos' || tab === 'settings' || tab === 'ranking') {
        selectedTab.value = tab;
        localStorage.setItem('selectedTab', tab);
      }
    };

    // 当页面加载时，检查 localStorage 中是否有用户的选择
    onMounted(() => {
      const storedTab = localStorage.getItem('selectedTab');
      if (storedTab) {
        selectedTab.value = storedTab;
      }
    });

    const refreshKeywords = async () => {
      isRefreshing.value = true;
      selectedKeyword.value = null;
      const response = await axios.get('http://localhost:5000/api/keywords');
      store.commit('setKeywords', response.data);
      isRefreshing.value = false;
    };

    const analyzeKeyword = async () => {
      if (!selectedKeyword.value) {
        ElMessage.warning('请先选择一个关键词');
        return;
      }

      keywordDetail.value = keywords.value.find(keyword => keyword[0] === selectedKeyword.value) || null;
      const response = await axios.get(`http://localhost:5000/api/videos?keyword=${selectedKeyword.value}`);
      relatedVideos.value = response.data;
    };

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

    const querySearch = (queryString: string, cb: (result: { value: string, weight: number }[]) => void) => {
      const results = keywords.value
        .map(keyword => ({ value: keyword[0], weight: keyword[1] }))
        .filter(keyword => queryString === '' || keyword.value.includes(queryString));
      cb(results);
    };

    const handleSelect = (item: { value: string }) => {
      selectedKeyword.value = item.value;
    };

    const analyzeSentiment = async () => {
      if (!selectedKeyword.value) {
        ElMessage.warning('请先选择一个关键词');
        return;
      }
      isRefreshing.value = true;
      const response = await axios.get(`http://localhost:5000/api/sentiment`, {
        params: {
          flag: 'keyword',
          value: selectedKeyword.value
        }
      });
      // 处理返回的数据，这里假设返回的数据是一个包含3个整型数的数组
      const sentimentData = response.data;
      console.log(sentimentData); // 或者你可以将数据存储在一个响应式变量中，然后在模板中显示
      isRefreshing.value = false;
    };



    return {
      analyzeSentiment,
      selectedTab,
      selectTab,
      keywords,
      RankingData,
      isRefreshing,
      refreshKeywords,
      analyzeKeyword,
      selectedKeyword,
      wordCloudImage,
      handleRowClick,
      keywordDetail,
      closeDetail,
      relatedVideos,
      handleImageError,
      getVideoInfo,
      querySearch,
      handleSelect // 添加这一行
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
  flex-direction: row;
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
</style>