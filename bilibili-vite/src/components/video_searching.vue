<template>
    <div>
        <el-dialog title="用户情感分析结果" v-model="sentimentAnalysisDialogVisible" width="50%" :append-to-body="true"
            v-draggable>
            <div class="dialog-content">
                <div ref="chart" style="height: 400px;"></div>
            </div>
            <template #footer>
                <!-- <span class="dialog-footer">
          <el-button @click="sentimentAnalysisDialogVisible = false">关闭</el-button>
        </span> -->
            </template>
        </el-dialog>
        <el-card class="box-card" style="margin-top: 70px; margin-left: 55px; width: 1425px;max-height: 90%;">
            <div class="video-info" style="display: flex; flex-direction: column; align-items: flex-start;">
                <div style="display: flex; align-items: flex-start;">
                    <el-input v-model="bvid" placeholder="请输入Bvid" @keyup.enter="searchVideo"
                        style="width: 200px; margin-right: 10px;"></el-input>
                    <el-button type="primary" @click="searchVideo">搜索</el-button>
                    <el-button type="primary" style="float: right; margin-right: 10px;"
                        @click="analyzeSentiment">用户情感分析</el-button>
                </div>
                <div v-if="videoInfo" style="margin-top: 10px; display: flex;">
                    <div style="flex: 1;">
                        <h1 class="video-title" style="text-align: left;">{{ videoInfo[7] }}</h1>
                        <div style="text-align: left;">
                            <iframe :src="`//player.bilibili.com/player.html?bvid=${videoInfo[0]}&poster=1&autoplay=0`"
                                scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"
                                width="675" height="405">
                            </iframe>
                        </div>
                        <hr
                            style="width: 675px; border-top: 0.5px; border-style: solid; border-color: rgb(227, 229, 231); box-shadow: 0 0 0.5px rgba(0, 0, 0, 0.5);">
                        <div v-if="videoInfo[10]" class="video-desc"
                            style="text-align: left; width: 675px; height: 100px; overflow-y: auto; white-space: pre-wrap; margin-top: 5px; background-color: white;">
                            {{ videoInfo[10] }}
                        </div>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: center;">
                        <el-table :data="[
                            { views: videoInfo[17], danmaku: videoInfo[18], reply: videoInfo[19], favorites: videoInfo[20] }
                        ]" style="width: 100%">
                            <el-table-column prop="views" label="观看数" :min-width="40" align="center"></el-table-column>
                            <el-table-column prop="danmaku" label="弹幕数" :min-width="40"
                                align="center"></el-table-column>
                            <el-table-column prop="reply" label="回复数" :min-width="40" align="center"></el-table-column>
                            <el-table-column prop="favorites" label="收藏数" :min-width="40"
                                align="center"></el-table-column>
                        </el-table>
                        <el-table :data="[
                            { coin: videoInfo[21], share: videoInfo[22], rank: videoInfo[24], like: videoInfo[25] }
                        ]" style="width: 100%">
                            <el-table-column prop="coin" label="硬币数" :min-width="40" align="center"></el-table-column>
                            <el-table-column prop="share" label="分享数" :min-width="40" align="center"></el-table-column>
                            <el-table-column prop="rank" label="历史最高排行" :min-width="60"
                                align="center"></el-table-column>
                            <el-table-column prop="like" label="点赞数" :min-width="40" align="center"></el-table-column>
                        </el-table>
                    </div>
                </div>
            </div>
        </el-card>
    </div>
</template>

<script lang="ts">
import { computed, ref, onMounted, watch, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';
import * as echarts from 'echarts';

export default {
    data() {
        return {
            bvid: '',
            videoInfo: null,
        };
    },
    methods: {
        async searchVideo() {
            try {
                const response = await axios.get('http://localhost:5000/api/specific_video', {
                    params: {
                        bvid: this.bvid,
                    },
                });
                this.videoInfo = response.data;
                console.log(response.data);

            } catch (error) {
                console.error(error);
            }
        },
    },
    setup() {
        const bvid = ref(''); // Define a ref for bvid
        const sentimentAnalysisDialogVisible = ref(false);
        const chart = ref(null);
        const analyzeSentiment = async () => {
            if (!bvid.value) {
                ElMessage.error('请先输入bvid');
                return; // 停止执行方法
            }

            try {
                // isRefreshing.value = true;
                const response = await axios.get(`http://localhost:5000/api/sentiment`, {
                    params: {
                        flag: 'bvid',
                        value: bvid.value,
                    }
                });
                console.log("Sentiment Data:", response.data);
                sentimentAnalysisDialogVisible.value = true; // 打开弹窗

                await nextTick(); // 等待 DOM 更新

                if (chart.value) {
                    // 检查并销毁已有的 ECharts 实例
                    if (echarts.getInstanceByDom(chart.value)) {
                        echarts.dispose(chart.value);
                    }
                    const data = response.data;
                    const [positive, neutral, negative] = data;
                    const chartInstance = echarts.init(chart.value);
                    const option = {
                        title: {
                            text: '情感分析',
                            subtext: '正向、中性、负向情感',
                            left: 'center'
                        },
                        tooltip: {
                            trigger: 'item'
                        },
                        legend: {
                            orient: 'vertical',
                            left: 'left',
                        },
                        series: [
                            {
                                name: '情感分布',
                                type: 'pie',
                                radius: '50%',
                                data: [
                                    { value: positive, name: '正向' },
                                    { value: neutral, name: '中性' },
                                    { value: negative, name: '负向' }
                                ],
                                label: {
                                    formatter: '{b}: {c} ({d}%)'
                                },
                                emphasis: {
                                    itemStyle: {
                                        shadowBlur: 10,
                                        shadowOffsetX: 0,
                                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                                    }
                                }
                            }
                        ]
                    };
                    chartInstance.setOption(option);
                } else {
                    console.error('Chart element not found or not ready for initialization.');
                }
            } catch (error) {
                console.error('Error during sentiment analysis:', error);
            } finally {
                // isRefreshing.value = false;
            }
        };
        return {
            analyzeSentiment,
            sentimentAnalysisDialogVisible,
            chart,
            bvid,
        };
    },
};
</script>

<style scoped>
.box-card {
    /* width: 30%; */
    box-shadow: 0 0 6px 2px lightblue !important;
    background-color: rgba(255, 255, 255, 0.85);
}

.video-title {
    font-size: 20px;
    font-family: PingFang SC, HarmonyOS_Regular, Helvetica Neue, Microsoft YaHei, sans-serif;
    font-weight: 500;
    -webkit-font-smoothing: antialiased;
    color: #18191C;
    line-height: 28px;
    margin-bottom: 6px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.video-desc {
    border: 2px solid rgba(0, 150, 255, 0.5);
    /* 淡蓝色半透明边框 */
    box-shadow: 0 0 10px rgba(0, 150, 255, 0.5);
    /* 淡蓝色半透明发光效果 */
    padding: 10px;
    /* 添加内边距 */
}

/* .dialog-content {
  display: flex;
  justify-content: center;
  align-items: center;
} */
</style>
