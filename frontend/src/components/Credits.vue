<template>
    <div>
        <a href="https://github.com/am1ter/">Flash decision v.{{ version }} © {{copyright_year}} Alexey Semyonov</a>
    </div>
</template>

<script>
    import { mapState } from "vuex"
    export default {
        name: "Credits",
        props: {},
        computed: {
            ...mapState(["version", "copyright_year"])
        }
    }
</script>

<style scoped>
    a {
        font-size: 16px;
    }

    @media (max-width: 380px) {
        a {
            font-size: 14px;
        }
    }
</style>