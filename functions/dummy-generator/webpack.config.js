module.exports = {
  entry: './dummy-generator.js',
  output: {
    path: __dirname,
    filename: 'dummy-generator.bundle.js',
  },
  target: 'node',
  mode: 'development',
};