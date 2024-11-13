<template>
  <div class="app">
    <header class="header">
      <h1>DeepFC 文件清理器</h1>
    </header>
    <main class="main">
      <FileList />
    </main>
  </div>
</template>

<script>
import FileList from './components/FileList.vue'

export default {
  name: 'App',
  components: {
    FileList
  }
}
</script>

<style>
body {
  margin: 0;
  background-color: #f5f7fa;
}

.app {
  min-height: 100vh;
}

.header {
  background-color: #409eff;
  color: white;
  padding: 1rem;
  text-align: center;
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}
</style> 