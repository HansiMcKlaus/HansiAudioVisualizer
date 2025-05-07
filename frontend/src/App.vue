<template>
  <div id="app">
    <nav class="mb-3 navbar navbar-expand-lg navbar-dark bg-black">
      <div class="container-fluid">
        <div class="navbar-nav mx-auto">
          <RouterLink to="/" class="nav-link">Home</RouterLink>
          <RouterLink to="/about" class="nav-link">About</RouterLink>
          <b-link href="https://github.com/HansiMcKlaus/HansiAudioVisualizer" target="_blank" class="nav-link">
            <i class="bi bi-github"></i>
          </b-link>
        </div>
      </div>
    </nav>
    <main class="mx-5">
      <RouterView />
    </main>
  </div>
</template>

<script>
import { RouterLink, RouterView } from 'vue-router'

export default {
  components: {
    RouterLink,
    RouterView
  }
}
</script>
<style scoped>
  :global(body) {
    background-color: #f8f8f8;
  }
</style>