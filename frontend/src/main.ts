import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import '@fontsource/press-start-2p/latin-400.css'
import '@fontsource/atkinson-hyperlegible/latin-400.css'
import '@fontsource/atkinson-hyperlegible/latin-700.css'
import './assets/main.css'
import './assets/immersion.css'
import './assets/frontloader.css'
import './assets/artwork.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
