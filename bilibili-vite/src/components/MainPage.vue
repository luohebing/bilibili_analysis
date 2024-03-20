<template>
    <el-container class="main-page" v-loading="state.isLoading" :element-loading-text="state.loadingMessage"
        element-loading-background="rgba(122, 122, 122, 0)">
        <el-header>
            <el-row type="flex" justify="center" align="middle">
                <el-col :span="24">
                    <h1 class="title"><img class="logo" src="/icon/logo.png" alt="Logo" />热点关注倾向实时分析</h1>
                </el-col>
            </el-row>
        </el-header>
        <el-main>
            <el-row type="flex" justify="center" align="middle" class="button-row">
                <el-col :span="24" class="button-col">
                    <el-button type="primary" @click="redirectToWordCloud" class="action-button">LinkStart</el-button>
                </el-col>
            </el-row>
        </el-main>
    </el-container>
</template>
  
<script lang="ts">
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useStore } from 'vuex';
import { key } from '../store';
import { reactive } from 'vue'; // 引入reactive

export default {
    setup() {
        const router = useRouter();
        const store = useStore(key);

        // 使用reactive创建响应式数据
        const state = reactive({
            title: 'Bilibili热点关注倾向实时分析',
            isLoading: false, // 加载状态
            loadingMessage: '' // 加载信息
        });

        const redirectToWordCloud = () => {
            state.isLoading = true; // 开始加载
            state.loadingMessage = '加载数据中...'; // 设置加载信息

            axios.get('http://localhost:5000/api/ranking')
                .then(response => {
                    store.commit('setRankingData', response.data);
                })
                .catch(error => {
                    console.log(error);
                });

            axios.get('http://localhost:5000/api/keywords')
                .then(response => {
                    // 将数据保存到 Vuex 或其他状态管理库中
                    // 然后在 WordCloud.vue 页面中读取这些数据
                    store.commit('setKeywords', response.data);
                    // console.log(response.data);

                    // 跳转到词云展示页面
                    router.push({ name: 'WordCloud' });
                })
                .catch(error => {
                    console.log(error);
                })
                .finally(() => {
                    state.isLoading = false; // 结束加载
                });
        };

        return {
            state,
            redirectToWordCloud
        };
    }
}
</script>
  
<style scoped>

.logo {
    /* margin-right: 0px; */
    transform: scale(0.8); 
}

.main-page {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
}

.title {
    font-size: 100px;
    color: rgb(0, 178, 255);
    text-align: center;
    margin-top: 130px;
    font-family: 'ZCOOL KuaiLe', cursive; /* 更改这里 */
    display: flex; /* 新增 */
    align-items: center; /* 新增 */
}

.action-button {
    width: 150px;
    /* 设置按钮宽度 */
    height: 50px;
    /* 设置按钮高度 */
    font-size: 25px;
    /* 设置字体加粗 */
    font-weight: bold;
    text-align: center;
    border-radius: 20px;
    /* 设置按钮边角圆润 */
    margin-top: 320px;
    /* 调整按钮与底部的距离 */
    font-family: 'Anta', cursive; /* 更改这里 */
}

.example-showcase .el-loading-mask {
    z-index: 9;
}
</style>