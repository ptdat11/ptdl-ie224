const esbuild = require('esbuild')

// Automatically exclude all node_modules from the bundled version
const { nodeExternalsPlugin } = require('esbuild-node-externals')

esbuild.build({
	entryPoints: ['./src/main.ts'],
	outfile: 'dist/index.js',
	bundle: true,
	minify: false,
	platform: 'node',
	sourcemap: true,
	target: 'node18',
	plugins: [nodeExternalsPlugin()]
})
	.catch(() => process.exit(1))