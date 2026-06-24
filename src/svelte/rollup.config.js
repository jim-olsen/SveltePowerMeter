import svelte from 'rollup-plugin-svelte';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import livereload from 'rollup-plugin-livereload';
import terser from '@rollup/plugin-terser';
import css from 'rollup-plugin-css-only'
import dev from 'rollup-plugin-dev'
//import serve from 'rollup-plugin-serve-proxy'

const production = !process.env.ROLLUP_WATCH;

const svelteInternalPathToken = 'node_modules/svelte/src/internal/';
const d3SelectionPathToken = 'node_modules/d3-selection/src/selection/';

function isSvelteInternalCircularWarning(warning) {
    if (warning.code !== 'CIRCULAR_DEPENDENCY') {
        return false;
    }

    if (warning.ids?.length) {
        return warning.ids.every((id) => id.includes(svelteInternalPathToken));
    }

    return warning.message?.includes(svelteInternalPathToken) || warning.importer?.includes(svelteInternalPathToken);
}

function isD3SelectionCircularWarning(warning) {
    if (warning.code !== 'CIRCULAR_DEPENDENCY') {
        return false;
    }

    if (warning.ids?.length) {
        return warning.ids.every((id) => id.includes(d3SelectionPathToken));
    }

    return warning.message?.includes(d3SelectionPathToken) || warning.importer?.includes(d3SelectionPathToken);
}

function isNodeModulesCircularWarning(warning) {
    if (warning.code !== 'CIRCULAR_DEPENDENCY') {
        return false;
    }

    if (warning.ids?.length) {
        return warning.ids.every((id) => id.includes('node_modules'));
    }

    return warning.message?.includes('node_modules/') || warning.importer?.includes('node_modules/');
}

function isNonBlockingSvelteWarning(warning) {
    if (warning.plugin === 'svelte') {
        return true;
    }

    return warning.message?.startsWith('Plugin svelte:') || warning.code?.startsWith('a11y_') || warning.code === 'script_unknown_attribute';
}

export default {
    input: 'src/main.js',
    output: {
        sourcemap: true,
        format: 'iife',
        name: 'app',
        file: 'public/bundle.js'
    },
    onwarn(warning, warn) {
        if (isSvelteInternalCircularWarning(warning) || isD3SelectionCircularWarning(warning) || isNodeModulesCircularWarning(warning) || isNonBlockingSvelteWarning(warning)) {
            return;
        }

        warn(warning);
    },
    plugins: [
        svelte({
            // enable run-time checks when not in production
            emitCss: true,
            compilerOptions: {
                dev: !production,
                compatibility: {
                    componentApi: 4
                }
            },
        }),

        css({"output": 'bundle.css'}),

        // If you have external dependencies installed from
        // npm, you'll most likely need these plugins. In
        // some cases you'll need additional configuration —
        // consult the documentation for details:
        // https://github.com/rollup/rollup-plugin-commonjs
        nodeResolve({
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
                },
                {
                    from: '/socket.io',
                    to: 'http://10.0.10.32:8050',
                    opts: {
                        websocket: true,
                        rewrite: (path) => path
                    }
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