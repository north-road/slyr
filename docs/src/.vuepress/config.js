const { description } = require('../../package')

module.exports = {
  title: 'SLYR Documentation',
  description: 'User Documentation for SLYR: the ESRI to QGIS Compatibility Suite',

  /**
   * Extra tags to be injected to the page HTML `<head>`
   *
   * ref：https://v1.vuepress.vuejs.org/config/#head
   */
  head: [
    ['meta', { name: 'theme-color', content: '#3eaf7c' }],
    ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
    ['meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black' }]
  ],

  locales: {
    '/': {
      lang: 'en-US',
      title: 'SLYR Documentation',
      description: 'User Documentation for SLYR: the ESRI to QGIS Compatibility Suite'
    }
  },

  /**
   * Theme configuration, here is the default theme configuration for VuePress.
   *
   * ref：https://v1.vuepress.vuejs.org/theme/default-theme-config.html
   */
  themeConfig: {
    repo: '',
    editLinks: false,
    displayAllHeaders: true,
    docsDir: 'docs/src',
    editLinkText: '',
    lastUpdated: true,
    sidebarDepth: 1,
    nav: [
      {
        text: 'North Road',
        link: 'https://north-road.com/slyr'
      }
    ],
    sidebar: require('./sidebar/en')
  },

  /**
   * Apply plugins，ref：https://v1.vuepress.vuejs.org/zh/plugin/
   */
  plugins: [
    '@vuepress/plugin-back-to-top',
    '@vuepress/plugin-medium-zoom',
  ]
}
