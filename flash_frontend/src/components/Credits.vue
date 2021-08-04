<template>
    <div>
        <a href='https://github.com/am1ter/'>Flash decision v.{{ version }} © 2021 Alexey Semyonov</a>
    </div>
</template>

<script>
    export default {
        name: 'Credits',
        props: {
            version: {
                type: String,
                required: true,
                default: '0.1.00'
                }
        }
    }
</script>

<style scoped>

</style>