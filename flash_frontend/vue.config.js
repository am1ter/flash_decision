module.exports = { 
    runtimeCompiler: false,
    parallel: true,
    devServer: {
        disableHostCheck: true,
        host: 'http://0.0.0.0',
        port: 8000,
        useLocalIp: true,
        https: false
    }
}