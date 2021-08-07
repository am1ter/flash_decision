<template>
    <div>
        <a href='https://github.com/am1ter/'>Flash decision v.{{ version }} © 2021 Alexey Semyonov</a>
    </div>
</template>

<script>
    import { mapState } from 'vuex'
    export default {
        name: 'Credits',
        props: {},
        computed: {
            ...mapState(['version'])
        }
    }
</script>

<style scoped>

</style>