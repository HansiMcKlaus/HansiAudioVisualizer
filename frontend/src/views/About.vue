<template>
  <div>
    <b-card class="about mx-auto">
      <p>This project initially began way back in 2021 when I wanted to visualize a short audio snipped for a video. Most video editing software supports this functionality in some capacity, but the one I used hid this feature behind a paywall. There are a lot of available tools to visualize audio out there, but basically everything I have found was used to render the visualization in real-time as the audio played in the background, which works for most use-cases, but not mine. I simply wanted to fully render out a visualization for further use in video editing, without having to screen-capture something for the entire duration of the audio.</p>
      <p>Thus began the first iteration with the name <a href="https://github.com/HansiMcKlaus/AudioSpectrumVisualizer" target="_blank">AudioSpectrumVisualizer</a>. It was an ugly mess, only made salvageable by the help of friends, and since it was solely CL based, not that user-friendly. Bonus points for a long audio file, which completely filled your RAM and crashed your machine. The project eventually broke and I was too lazy to fix it.</p>
      <p>Now, a bit more than three years wiser, if none the smarter, I restarted the project, added a visual interface, expanded the visualizations and hopefully created a bit less ugly project in the process.</p>
    </b-card>
  </div>
</template>

<script>
export default {
  data() {
    return {
    }
  },
  methods: {
  },
}
</script>

<style scoped>
.about {
  max-width: 1000px;
}
</style>