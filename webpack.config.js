const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';

  return {
    entry: {
      // Bundle all JavaScript files into a single optimized bundle
      bundle: [
        './static/js/api.js',
        './static/js/theme-manager.js',
        './static/js/market-status.js',
        './static/js/global-search.js',
        './static/js/notifications.js',
        './static/js/charts.js',
        './static/js/components.js',
        './static/js/export-manager.js',
        './static/js/dashboard-customizer.js',
        './static/js/app.js'
      ],

      // Separate bundle for heavy analysis features (lazy loaded)
      'analysis': [
        './static/js/technical-charts.js',
        './static/js/advanced-chart.js',
        './static/js/ai-analysis.js'
      ],

      // Separate bundle for dashboard widgets
      'dashboard-widgets': [
        './static/js/dashboard-charts.js',
        './static/js/market-indices.js',
        './static/js/mini-charts.js',
        './static/js/websocket-manager.js'
      ],

      // Admin bundle (separate page)
      'admin': [
        './static/js/admin.js',
        './static/js/admin-init.js'
      ]
    },

    output: {
      filename: '[name].min.js',
      path: path.resolve(__dirname, 'static/dist'),
      publicPath: '/static/dist/'
    },

    optimization: {
      minimize: isProduction,
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: false, // Keep console.logs for debugging
              pure_funcs: [],
              dead_code: true,
              unused: true
            },
            mangle: {
              // Preserve global function names that are called from HTML
              reserved: [
                'StockAnalyzerApp',
                'AIAnalysisVisualizer',
                'ThemeManager',
                'MarketStatusWidget',
                'MarketIndicesWidget',
                'ExportManager',
                'DashboardCustomizer',
                'TechnicalChartsManager',
                'AdvancedChart',
                'WebSocketManager',
                'api',
                'app'
              ]
            },
            format: {
              comments: false
            }
          },
          extractComments: false
        })
      ]
    },

    // No module resolution needed - just concatenate and minify
    module: {
      rules: []
    },

    // Performance hints
    performance: {
      hints: isProduction ? 'warning' : false,
      maxEntrypointSize: 300000, // 300 KB per entry point
      maxAssetSize: 300000
    },

    // Stats configuration
    stats: {
      assets: true,
      chunks: true,
      modules: false,
      entrypoints: true,
      colors: true
    },

    // Development tools
    devtool: isProduction ? false : 'source-map'
  };
};
