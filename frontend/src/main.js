import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import 'bootstrap-icons/font/bootstrap-icons.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import { BootstrapVue3 } from 'bootstrap-vue-3'
import ToastPlugin from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-default.css'

const app = createApp(App)

app.use(router)
app.use(BootstrapVue3)
app.use(ToastPlugin)

app.mount('#app')
