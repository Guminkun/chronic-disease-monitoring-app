<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">权限管理</h2>
        <p class="text-gray-500 mt-1">管理用户角色和权限分配</p>
      </div>
      <el-button type="primary" class="!bg-primary" :icon="Plus">新建角色</el-button>
    </div>

    <!-- Role Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Super Admin -->
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
              超级管理员
              <el-tag size="small" type="info" effect="plain">系统默认</el-tag>
            </h3>
            <p class="text-gray-500 text-sm mt-1">拥有系统所有权限</p>
          </div>
          <div class="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center text-blue-500">
            <el-icon class="text-2xl"><Lock /></el-icon>
          </div>
        </div>
        
        <div class="space-y-3 py-4 border-t border-b border-gray-50 my-4">
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">拥有权限</span>
            <span class="font-medium text-gray-900">6</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">用户数</span>
            <span class="font-medium text-gray-900">2</span>
          </div>
        </div>

        <div class="flex gap-3">
          <el-button class="flex-1" :icon="Edit">编辑</el-button>
          <el-button class="flex-1" type="danger" plain :icon="Delete">删除</el-button>
        </div>
      </div>

      <!-- Medical Staff -->
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-bold text-gray-900">医疗事务员</h3>
            <p class="text-gray-500 text-sm mt-1">负责医生资质审核和验证</p>
          </div>
          <div class="w-12 h-12 rounded-lg bg-green-50 flex items-center justify-center text-green-500">
            <el-icon class="text-2xl"><FirstAidKit /></el-icon>
          </div>
        </div>
        
        <div class="space-y-3 py-4 border-t border-b border-gray-50 my-4">
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">拥有权限</span>
            <span class="font-medium text-gray-900">3</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">用户数</span>
            <span class="font-medium text-gray-900">5</span>
          </div>
        </div>

        <div class="flex gap-3">
          <el-button class="flex-1" :icon="Edit">编辑</el-button>
          <el-button class="flex-1" type="danger" plain :icon="Delete">删除</el-button>
        </div>
      </div>

      <!-- Data Manager -->
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-bold text-gray-900">数据管理员</h3>
            <p class="text-gray-500 text-sm mt-1">管理系统数据和统计报表</p>
          </div>
          <div class="w-12 h-12 rounded-lg bg-purple-50 flex items-center justify-center text-purple-500">
            <el-icon class="text-2xl"><DataBoard /></el-icon>
          </div>
        </div>
        
        <div class="space-y-3 py-4 border-t border-b border-gray-50 my-4">
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">拥有权限</span>
            <span class="font-medium text-gray-900">4</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">用户数</span>
            <span class="font-medium text-gray-900">3</span>
          </div>
        </div>

        <div class="flex gap-3">
          <el-button class="flex-1" :icon="Edit">编辑</el-button>
          <el-button class="flex-1" type="danger" plain :icon="Delete">删除</el-button>
        </div>
      </div>

      <!-- Support Team -->
      <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm transition-transform hover:-translate-y-1 hover:shadow-lg">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-bold text-gray-900">支持团队</h3>
            <p class="text-gray-500 text-sm mt-1">提供用户支持和问题解决</p>
          </div>
          <div class="w-12 h-12 rounded-lg bg-orange-50 flex items-center justify-center text-orange-500">
            <el-icon class="text-2xl"><Headset /></el-icon>
          </div>
        </div>
        
        <div class="space-y-3 py-4 border-t border-b border-gray-50 my-4">
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">拥有权限</span>
            <span class="font-medium text-gray-900">3</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">用户数</span>
            <span class="font-medium text-gray-900">8</span>
          </div>
        </div>

        <div class="flex gap-3">
          <el-button class="flex-1" :icon="Edit">编辑</el-button>
          <el-button class="flex-1" type="danger" plain :icon="Delete">删除</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Plus, Edit, Delete, Lock, FirstAidKit, DataBoard, Headset } from '@element-plus/icons-vue'
</script>
