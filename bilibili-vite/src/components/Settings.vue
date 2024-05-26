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
            <el-menu-item index="ranking" @click="navigateToRanking">热门内容</el-menu-item>
            <el-sub-menu index="analysis">
                <template #title><b>分析模式</b></template>
                <el-menu-item index="keywords" @click="navigateToWordCloud">关键词分析</el-menu-item>
                <el-menu-item index="videos" @click="navigateToWordCloud">视频分析</el-menu-item>
            </el-sub-menu>
            <!-- <el-menu-item index="settings">设置</el-menu-item> -->
            <el-menu-item index="settings">
                设置
            </el-menu-item>
        </el-menu>
        <div class="overlay" v-show="isRefreshing"></div>

        <div v-if="selectedTab === 'settings'">
            <!-- 设置相关的元素 -->
            <el-card class="box-card" style="margin-top: 100px;position:absolute;left:10%;width:80%; max-height: 80%;">
                <div slot="header" class="clearfix">
                    <span><b>设置</b></span>
                </div>
                <div class="setting-item">
                    <el-tooltip content="包含进行情感分析时缓存到本地的视频评论、弹幕等数据。" placement="top">
                        <div class="setting-title"><b>情感分析语料缓存</b></div>
                    </el-tooltip>
                    <div class="setting-actions">
                        <span>{{ emotionCacheSize }}</span>
                        <el-button type="primary" @click="calculateEmotionCacheSize">计算缓存大小</el-button>
                        <el-button type="danger" @click="clearEmotionCache">清空缓存</el-button>
                    </div>
                </div>
                <div class="setting-item">
                    <el-tooltip content="包含热门视频封面图片文件缓存，删除后浏览视频时会重新加载。" placement="top">
                        <div class="setting-title"><b>视频封面缓存</b></div>
                    </el-tooltip>
                    <div class="setting-actions">
                        <span>{{ videoCacheSize }}</span>
                        <el-button type="primary" @click="calculateVideoCacheSize">计算缓存大小</el-button>
                        <el-button type="danger" @click="clearVideoCache">清空缓存</el-button>
                    </div>
                </div>
                <div class="setting-item">
                    <el-tooltip content="包含热门视频的标题、简介、标签、播放量等数据，分析系统的必要前提。" placement="top">
                        <div class="setting-title"><b>热门稿件数据</b></div>
                    </el-tooltip>
                    <div class="setting-actions">
                        <el-tooltip content="从b站获取最新热门数据，转储需要一定时间内。" placement="top">
                            <el-button type="warning" @click="updateRanking" v-loading="isRefreshing">更新</el-button>
                        </el-tooltip>
                    </div>
                </div>
            </el-card>

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
            emotionCacheSize: '',
            videoCacheSize: ''
        };
    },
    methods: {
        navigateToMainpage() {
            this.$router.push({ name: 'MainPage' }); // 使用路由的名称导航到 Mainpage.vue
        },
        navigateToWordCloud() {
            this.$router.push({ name: 'WordCloud' }); // 使用路由的名称导航到 WordCloud.vue
        },
        navigateToRanking() {
            this.$router.push({ name: 'Ranking' }); // 使用路由的名称导航到 Ranking.vue
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
        calculateEmotionCacheSize() {
            // 向后端发送请求计算情感分析语料缓存大小
            axios.get('http://localhost:5000/api/emotion/cache/size')
                .then(response => {
                    this.emotionCacheSize = response.data;
                })
                .catch(error => {
                    console.error('Error calculating emotion cache size: ', error);
                });
        },
        clearEmotionCache() {
            // 向后端发送请求清空情感分析语料缓存
            axios.get('http://localhost:5000/api/emotion/cache/clear')
                .then(response => {
                    this.emotionCacheSize = response.data;
                })
                .catch(error => {
                    console.error('Error clearing emotion cache: ', error);
                });
        },
        calculateVideoCacheSize() {
            // 向后端发送请求计算视频封面缓存大小
            axios.get('http://localhost:5000/api/video/cache/size')
                .then(response => {
                    this.videoCacheSize = response.data;
                })
                .catch(error => {
                    console.error('Error calculating video cache size: ', error);
                });
        },
        clearVideoCache() {
            // 向后端发送请求清空视频封面缓存
            axios.get('http://localhost:5000/api/video/cache/clear')
                .then(response => {
                    this.videoCacheSize = response.data;
                })
                .catch(error => {
                    console.error('Error clearing video cache: ', error);
                });
        }
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

        const updateRanking = () => {
            isRefreshing.value = true;
            axios.get('http://localhost:5000/api/updateranking')
                .then(() => {
                    // 请求完成后
                    isRefreshing.value = false;
                })
                .catch(error => {
                    console.error('发送请求时出错：', error);
                    // 如果请求出错也要设置为 false
                    isRefreshing.value = false;
                });
        }



        return {
            updateRanking,
            analyzeSentiment,
            selectedTab,
            selectTab,
            keywords,
            RankingData,
            isRefreshing,
            refreshKeywords,
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

.setting-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    transition: background-color 0.3s;
    /* 添加过渡效果 */
    padding: 5px;
    /* 添加 padding 来留出边距 */
    border-radius: 10px;
    /* 添加圆角 */
}

.setting-item:hover {
    background-color: rgba(173, 216, 230, 0.5);
    /* 鼠标 hover 时的背景颜色，可以根据需要调整 */
}

.setting-title {
    flex: 1;
    margin-right: 10px;
    text-align: left;
}

.setting-actions {
    display: flex;
    align-items: center;
}

.setting-actions>* {
    margin-left: 10px;
}
</style>