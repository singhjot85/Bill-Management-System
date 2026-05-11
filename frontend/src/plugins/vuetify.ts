import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#6366f1',
          secondary: '#10b981',
          surface: '#ffffff',
          background: '#f8fafc',
        },
      },
      dark: {
        colors: {
          primary: '#6366f1',
          secondary: '#10b981',
          surface: '#1e293b',
          background: '#0f172a',
        },
      },
    },
  },
})
