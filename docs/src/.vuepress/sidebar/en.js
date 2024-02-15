module.exports = {
      '/': [
        {
            title: 'Get started',
            collapsable: false,
            sidebarDepth: 0,
            children: [
                '/user_guide/pricing',
                '/user_guide/installation',
                '/user_guide/configuring',
            ]
        },
        {
            title: 'Available tools',
            collapsable: true,
            sidebarDepth: 1,
            children: [
                '/user_guide/tools',
            ]
        }
      ]
}