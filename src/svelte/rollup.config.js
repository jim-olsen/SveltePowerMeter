import svelte from 'rollup-plugin-svelte';
import resolve from 'rollup-plugin-node-resolve';
import commonjs from 'rollup-plugin-commonjs';
import livereload from 'rollup-plugin-livereload';
import { terser } from 'rollup-plugin-terser';
import css from 'rollup-plugin-css-only'
import dev from 'rollup-plugin-dev'
//import serve from 'rollup-plugin-serve-proxy'

const production = !process.env.ROLLUP_WATCH;

export default {
    input: 'src/main.js',
    output: {
        sourcemap: true,
        format: 'iife',
        name: 'app',
        file: 'public/bundle.js'
    },
    plugins: [
        svelte({
            // enable run-time checks when not in production
            dev: !production,
            // we'll extract any component CSS out into
            // a separate file — better for performance
            css: css => {
                css.write('public/bundle.css');
            }
        }),

        css({"output": 'bundle.css'}),

        // If you have external dependencies installed from
        // npm, you'll most likely need these plugins. In
        // some cases you'll need additional configuration —
        // consult the documentation for details:
        // https://github.com/rollup/rollup-plugin-commonjs
        resolve({
            browser: true,
            dedupe: importee => importee === 'svelte' || importee.startsWith('svelte/')
        }),
        commonjs(),

        // Watch the `public` directory and refresh the
        // browser on changes when not in production
        !production && livereload('public'),

        // If we're building for production (npm run build
        // instead of npm run dev), minify
        production && terser(),

        !production && dev({
            dirs: ['public'],
            spa: 'public/index.html',
            host: '0.0.0.0',
            port: 8080,
            proxy: [
                {
                from: '/graphData',
                to: 'http://10.0.10.32:8050/graphData'
                },
                {
                    from: '/currentData',
                    to: 'http://10.0.10.32:8050/currentData'
                },
                {
                    from: '/statsData',
                    to: 'http://10.0.10.32:8050/statsData'
                },
                {
                    from: '/starlink',
                    to: 'http://10.0.10.32:8050/starlink'
                },
                {
                    from: '/shelly',
                    to: 'http://10.0.10.32:8050/shelly'
                },
                {
                    from: '/blueIrisAlert',
                    to: 'http://10.0.10.32:8050/blueIrisAlert'
                },
                {
                    from: '/adsbData',
                    to: 'http://10.0.10.32:8050/adsbData'
                },
                {
                    from: '/weatherData',
                    to: 'http://10.0.10.32:8050/weatherData'
                },
                {
                    from: '/weatherDailyMinMax',
                    to: 'http://10.0.10.32:8050/weatherDailyMinMax'
                },
                {
                    from: '/graphWxData',
                    to: 'http://10.0.10.32:8050/graphWxData'
                },
                {
                    from: '/batteryData',
                    to: 'http://10.0.10.32:8050/batteryData'
                },
                {
                    from: '/graphBatteryData',
                    to: 'http://10.0.10.32:8050/graphBatteryData'
                },
                {
                    from: '/shelly/relay/on',
                    to: 'http://10.0.10.32:8050/shelly/relay/on'
                },
                {
                    from: '/shelly/relay/off',
                    to: 'http://10.0.10.32:8050/shelly/relay/off'
                },
                {
                    from: '/lightningData',
                    to: 'http://10.0.10.32:8050/lightningData'
                }
                ]
        })
//        !production && serve({
//            contentBase: ['public'],
//            host: 'localhost',
//            port: 8080,
//            proxy: {
//                starlink: 'http://localhost:9999'
//            }
//        })
    ],
    watch: {
        clearScreen: false
    }
};