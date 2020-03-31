# Hello

This is a test file

<!-- webpack.config.js:eNpdkMFuwjAQRO98xQhVMkhpcg/qiRvXHCkCkyytkWOnXoeCEP/etQG16sXyeN/OrLf1jiMGHT/xhkBfowk0U0mr+WIy6X03WirpPPgQWZDrBCAXw6WGKisObWVcR+fyyKqQkh/jMMY6Y8DBWHK6J2F7bdwTQs6r81kGYm9PNNtuOxMSXEB1hqOaJ/SWjvsQT9Mgd66xzgKoKnC8pHIbSEdi7LLewflO1CH4HqtGoGDcBy/QsnTHoB3bjC+bBsZFj6Xve+9WzQKsE9P6fpAPMBqRSEAjtcFzzBbaWv+d5RB8S8xij5PR0GP0Q6CDOVN4DHmFJMlaqveSpfmlMgVGlpnXUHnaV+t1R0EVgBLgr0zD/Gr1yH++bO4r+hdylIgCdG7t2ElKlVaxva+RpXDvrTHd6z3Zh9UUt2y0eez9tpj8APiNrXU= -->

## Hello2

Some more content:

- Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
- tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
- quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
- consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse

`fisch/asd.json`:

```
const path = require('path');

module.exports = {
  entry: './src/index.js',
  output: {
    filename: 'main.js',
    path: path.resolve(__dirname, 'dist'),
  },
  module: {
    rules: [
      // style: creates `style` nodes from JS strings; css: translates CSS into CommonJS; sass: compiles Sass to CSS; postcss: allow postprocessing via autoprefixer
      { test: /\.scss$/i, use: [ 'style-loader',  'css-loader',  'sass-loader', 'postcss-loader'] },
      { test: /\.js$/, exclude: /node_modules/, loader: "babel-loader" }
    ],
  },
};
```

## Huhu3

```
const path = require('path');
```
