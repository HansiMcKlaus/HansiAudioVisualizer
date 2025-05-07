<template>
  <div>
    <b-card>
      <b-row
        style="font-size: 20px;">
        <b-col cols="12" lg="6">
          <div
            class="border mx-auto text-center d-block"
            :class="isDragging && 'border-primary'"
            @dragover.prevent
            @dragenter.prevent="isDragging = true"
            @dragleave="isDragging = false"
            @drop.prevent="onAudioDrop">
            <input
              type="file"
              name="audioInput"
              id="audioInput"
              class="d-none"
              accept="audio/*"
              @change="onAudioSelect"/>
            <label for="audioInput" class="w-100 p-2" style="cursor: pointer">
              <div v-if="isDragging">Drop file here</div>
              <div v-else>Drop audio file or click to select</div>
            </label>
          </div>
        </b-col>
        <b-col cols="12" lg="6">
          <b-form-input
            class="h-100"
            type="text"
            placeholder="Ex: https://www.youtube.com/watch?v=cvaIgq5j2Q8"
            v-model.trim="videoURL"
            @input="getAudioMetaDataFromURL()" />
        </b-col>
      </b-row>
      <div v-if="audioFile || isVideoURLValid" class="mt-3 d-flex justify-content-center align-items-center">
        <div class="mx-2">
          <img :src="metaData.coverImage || noCoverImage" alt="Cover Art" draggable="false" class="rounded-circle object-fit-cover" style="width: 50px; height: 50px; " />
        </div>
        <audio v-if="audioFile" controls onloadstart="this.volume=0.5" :src="audioSource"></audio>
        <div class="mx-2"><b>Title:</b> {{ metaData.title }}</div>
        <div v-if="audioFile" class="mx-2"><b>Artist:</b> {{ metaData.artist }}</div>
        <div v-if="isVideoURLValid" class="mx-2"><b>Uploader:</b> {{ metaData.uploader }}</div>
        <div class="mx-2"><b>Duration:</b> {{ formatedDuration() }}</div>
        <div v-if="audioFile" class="mx-2"><b>File:</b> {{ audioFile.name }}</div>
      </div>
    </b-card>
  </div>
</template>

<script>
import { useToast } from 'vue-toast-notification'

import { getYTMetaData } from "@/api"
import { parseBlob } from "music-metadata"
import noCoverImage from "@/assets/NoCoverImage.png"

export default {
  data() {
    return {
      noCoverImage,
      isDragging: false,
      audioFile: null,
      audioSource: null,
      videoURL: null,
      isVideoURLValid: false,
      metaData: {
        title: null,
        artist: null,
        uploader: null,
        duration: null,
        coverImage: null,
      }
    }
  },
  methods: {
    createToast(message, variant = "default") {
      const toast = useToast()
      toast.open({
        message: message,
        type: variant,
        closeOnClick: true,
        position: "top-right",
        pauseOnFocusLoss: true,
        pauseOnHover: true,
        duration: 3000,
        dismissible: true,
      })
    },
    onAudioSelect (event) {
      const file = event.target.files[0]
      this.handleAudioChange(file)
    },
    onAudioDrop (event) {
      const file = event.dataTransfer.files[0]
      this.handleAudioChange(file)
      this.isDragging = false
    },
    async handleAudioChange (file) {
      if (file && file.type.startsWith('audio/')) {
        this.resetMetaData()
        this.videoURL = null
        this.isVideoURLValid = false
        this.audioFile = file
        this.audioSource = URL.createObjectURL(file)
        await this.getAudioMetaData(file)
        this.$emit('audio-selected', { audioFile: this.audioFile, duration: this.metaData.duration })
      } else {
        this.createToast("Please select a valid audio file.", "error")
      }
    },
    async getAudioMetaData (file) {
      try {
        const metadata = await parseBlob(file)

        this.metaData.title = metadata.common.title || "Unknown Title"
        this.metaData.artist = metadata.common.artist || "Unknown Artist"
        this.metaData.duration = Math.ceil(metadata.format.duration) || null

        if (metadata.common.picture && metadata.common.picture.length > 0) {
          const cover = metadata.common.picture[0]
          const base64String = `data:${cover.format};base64,${btoa(String.fromCharCode(...new Uint8Array(cover.data)))}`
          this.metaData.coverImage = base64String
        } else {
          this.metaData.coverImage = null
        }
      } catch (error) {
        this.createToast("Error extracting audio metadata:" + error, "error")
      }
    },
    async getAudioMetaDataFromURL () {
      this.resetMetaData()
      this.audioFile = null
      this.isVideoURLValid = false
      if (this.videoURL.length >= 11) {
        try {
          const metadata = await getYTMetaData(this.videoURL)
          this.isVideoURLValid = true
          if (metadata) {
            this.metaData.title = metadata.title|| "Unknown Title"
            this.metaData.uploader = metadata.uploader|| "Unknown Uploader"
            this.metaData.duration = Math.ceil(metadata.duration) || null
            this.metaData.coverImage = metadata.thumbnail || null
            this.$emit('audio-selected-from-url', { videoURL: this.videoURL, title: this.metaData.title, duration: this.metaData.duration, id: metadata.id })
          }
        } catch (error) {
          this.isVideoURLValid = false
          this.createToast("Not a valid URL", "error")
        }
      }
    },
    resetMetaData () {
      this.metaData.title = null
      this.metaData.artist = null
      this.metaData.uploader = null
      this.metaData.duration = null
      this.metaData.coverImage = null
      this.metaData.title = null
    },
    formatedDuration () {
      if (this.metaData.duration && this.metaData.duration > 0) {
        const hours = Math.floor(this.metaData.duration / 3600)
        const minutes = Math.floor(this.metaData.duration / 60 % 60)
        const seconds = Math.floor(this.metaData.duration % 60)

        const formattedHours = hours > 0 ? `${hours}:` : ""
        const formattedMinutes = (minutes < 10 && hours > 0) ? `0${minutes}` : minutes
        const formattedSeconds = seconds < 10 ? `0${seconds}` : seconds

        return `${formattedHours}${formattedMinutes}:${formattedSeconds}`
      } else {
        return "Unknown Duration"
      }
    },
  },
}
</script>
