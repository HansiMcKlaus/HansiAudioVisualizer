<template>
  <div>
    <audio-selection
      @audio-selected="onAudioSelected"
      @audio-selected-from-url="onAudioSelectedFromURL" />
    <settings
      :audio-duration="audioDuration"
      :audio-selection="audioSelection"
      :audio-file-name="audioFileName"
      @settings-changed="onSettingsChanged"
      class="mt-3" />
    <b-row>
      <b-col cols="3">
        <b-card class="mt-3">
          <b-card-title>
            <b-button
              v-if="false"
              variant="primary"
              @click="generatePreview">
              Generate Preview Image
            </b-button>
          </b-card-title>
          <div v-if="isGeneratingPreview">Generating Preview</div>
          <img
            v-if="previewImage"
            :src="previewImage"
            alt="Preview Image"
            class="img-fluid mw-100"
            style="max-height: 300px;" />
        </b-card>
      </b-col>
      <b-col cols="9">
        <b-card class="mt-3">
          <b-card-title>
            <div class="d-flex gap-3">
              <b-button
                variant="primary"
                :disabled="!selectedAudioFile && !audioURL"
                @click="generateVideo()">
                Generate Video
              </b-button>
              <b-button
                v-if="generatedVideoPath"
                variant="primary"
                @click="downloadVideo()">
                Download Video
              </b-button>
            </div>
          </b-card-title>
          <div>
            <div v-if="isUploading">Downloading Audio</div>
            <div v-if="isGenerating">Generating Video</div>
            <video v-if="generatedVideoPath" controls onloadstart="this.volume=0.5" class="mw-100">
              <source :src="generatedVideoPath" type="video/mp4">
              Your browser does not support the video tag.
            </video>
          </div>
        </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import _ from "lodash"
import { useToast } from 'vue-toast-notification'
import { uploadAudio, uploadAudioFromURL, generateVideo, generatePreviewImage, downloadVideo } from "@/api"

import AudioSelection from '@/components/AudioSelection.vue'
import Settings from '@/components/Settings.vue'

export default {
  components: {
    AudioSelection,
    Settings,
  },
  data() {
    return {
      audioSelection: null,
      selectedAudioFile: null,
      audioURL: null,
      audioURLId: null,
      audioFileName: null,
      audioDuration: null,
      settings: {},
      isGeneratingPreview: false,
      previewImage: null,
      isUploading: false,
      isGenerating: false,
      generatedVideoPath: null,
      debouncedGeneratePreview: null,
    }
  },
  methods: {
    createToast(message, variant = "default") {
      const toast = useToast()
      toast.open({
        message: message,
        type: variant,
        closeOnClick: true,
        position: "bottom",
        pauseOnFocusLoss: true,
        pauseOnHover: true,
        duration: 3000,
        dismissible: true,
      })
    },
    onAudioSelected (audio) {
      this.audioSelection = "file"
      this.selectedAudioFile = audio.audioFile
      this.audioFileName = audio.audioFile.name
      this.audioDuration = audio.duration
    },
    onAudioSelectedFromURL (audio) {
      this.audioSelection = "url"
      this.audioURL = audio.videoURL
      this.audioURLId = audio.id
      this.audioFileName = audio.title
      this.audioDuration = audio.duration
    },
    onSettingsChanged (settings) {
      this.settings = settings
      this.debouncedGeneratePreview()
    },
    async generatePreview () {
      this.previewImage = null
      this.isGeneratingPreview = true
      try {
        const response = await generatePreviewImage(this.settings)
        
        if (response) {
          const blob = new Blob([response.data], { type: 'image/png' })
          this.previewImage = URL.createObjectURL(blob)
        } else {
          this.createToast("Preview image not received", "error")
        }
      } catch (error) {
        this.createToast("Preview image not received:" + error, "error")
      }
      this.isGeneratingPreview = false
    },
    async uploadAudio () {
      const formData = new FormData()
      formData.append("file", this.selectedAudioFile)

      try {
        const uploadResponse = await uploadAudio(formData)
      } catch (error) {
        this.createToast("Error uploading audio:" + error, "error")
      }
    },
    async uploadAudioFromURL () {
      try {
        const uploadResponse = await uploadAudioFromURL(this.audioURLId)
      } catch (error) {
        this.createToast("Error uploading audio:" + error, "error")
      }
    },
    async generateVideo () {
      this.generatedVideoPath = null
      this.isUploading = true
      if (this.audioSelection === "file") {
        await this.uploadAudio()
      } else if (this.audioSelection === "url") {
        await this.uploadAudioFromURL()
      }
      this.isUploading = false

      this.isGenerating = true
      try {
        let response
        if (this.audioSelection === "file") {
          response = await generateVideo(this.selectedAudioFile.name, this.settings)
        } else if (this.audioSelection === "url") {
          response = await generateVideo(this.audioURLId + ".mp3", this.settings)
        }
        if (response.data.video_url) {
          this.generatedVideoPath = response.data.video_url
        } else {
          this.createToast("Video URL not received", "error")
        }
      } catch (error) {
        this.createToast("Video URL not received:" + error, "error")
      }
      this.isGenerating = false
    },
    async downloadVideo () {
      if (!this.generatedVideoPath) {
        return
      } else {
        let filename = this.generatedVideoPath.split("/").pop().split("?")[0]
        filename = decodeURIComponent(filename)
        try {
          await downloadVideo(filename)
        } catch (error) {
          this.createToast("Error downloading video:" + error, "error")
        }
      }
    },
  },
  created() {
    this.debouncedGeneratePreview = _.debounce(this.generatePreview, 500)
  },
  mounted() {
  },
}
</script>
