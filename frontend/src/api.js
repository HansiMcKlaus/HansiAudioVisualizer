import axios from "axios"

const apiClient = axios.create({
  baseURL: "http://127.0.0.1:8000",
})

export const getYTMetaData = async (videoURL) => {
  const response = await apiClient.post("/get-yt-meta-data", {
    videoURL,
  })

  return response.data
}

export const uploadAudio = async (formData) => {
  const response = await apiClient.post("/upload-audio", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  })

  return response
}

export const uploadAudioFromURL = async (audioURLId) => {
  const response = await apiClient.post("/upload-audio-from-url", {
    audioURLId,
  })

  return response
}

export const generatePreviewImage = async (settings) => {
  const response = await apiClient.post("/generate-preview-image", {
    settings: settings,
  }, {
    responseType: 'arraybuffer'
  })

  return response
}

export const generateVideo = async (filename, settings) => {
  const response = await apiClient.post("/generate-video", {
    filename,
    settings,
  })

  return response
}

export const downloadVideo = async (filename) => {
  const response = await apiClient.get(`/download-video/${filename}`, {
    responseType: "blob",
  })

  const blob = new Blob([response.data], { type: "video/mp4" })

  const link = document.createElement("a")
  link.href = URL.createObjectURL(blob)
  link.setAttribute("download", filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}