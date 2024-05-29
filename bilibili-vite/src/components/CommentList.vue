<template>
    <div>
        <el-scrollbar style="height: 300px;">
            <ul>
                <li v-for="(comment, index) in currentPageComments" :key="index">
                    <div>{{ comment[0] }}</div>
                    <div style="text-align: right;">点赞数: {{ comment[1] }}</div>
                </li>
            </ul>
        </el-scrollbar>
        <el-pagination @current-change="handlePageChange" :page-sizes="[5]" :page-size="pageSize"
            layout="sizes, prev, pager, next" :total="commentCount" style="margin-top: 10px;"></el-pagination>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
export default defineComponent({
    name: 'CommentList',
    props: {
        videoReply: {
            type: Array,
            required: true,
        },
        currentPage: {
            type: Number,
            default: 1,
        },
        pageSize: {
            type: Number,
            default: 5,
        },
    },
    data() {
        return {
            commentCount: this.videoReply.length,
        };
    },
    computed: {
        currentPageComments() {
            const startIndex = (this.currentPage - 1) * this.pageSize;
            const endIndex = startIndex + this.pageSize;
            return this.videoReply.slice(startIndex, endIndex);
        },
    },
    methods: {
        handlePageChange(newPage) {
            this.$emit('update:currentPage', newPage);
        },
    },
});
</script>