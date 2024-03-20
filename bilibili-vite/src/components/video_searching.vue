<template>
    <div>
        <el-card class="box-card" style="margin-top: 70px; margin-left: 55px; width: 1425px;max-height: 90%;">
            <div class="video-info" style="display: flex; flex-direction: column; align-items: flex-start;">
                <div style="display: flex; align-items: flex-start;">
                    <el-input v-model="bvid" placeholder="请输入Bvid" @keyup.enter="searchVideo"
                        style="width: 200px; margin-right: 10px;"></el-input>
                    <el-button type="primary" @click="searchVideo">搜索</el-button>
                </div>
                <div v-if="videoInfo" style="margin-top: 10px; display: flex;">
                    <div style="flex: 1;">
                        <h1 class="video-title" style="text-align: left;">{{ videoInfo[7] }}</h1>
                        <iframe :src="`//player.bilibili.com/player.html?bvid=${videoInfo[0]}&poster=1&autoplay=0`"
                            scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"
                            width="675" height="405">
                        </iframe>
                        <hr
                            style="width: 675px; border-top: 0.5px; border-style: solid; border-color: rgb(227, 229, 231); box-shadow: 0 0 0.5px rgba(0, 0, 0, 0.5);">
                        <div class="video-desc"
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
import axios from 'axios';

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
</style>
