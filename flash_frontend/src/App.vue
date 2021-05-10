<template>
    <div id="app">
        <Header/>
        <Title title="Flash decision v.0.3" :page_name='page_name'/>
        <router-view>
            <Start/>
            <Terminal/>
            <Scoreboard/>
        </router-view>
    </div>
</template>

<script>
    import Header from './components/Header.vue'
    import Title from './components/Title.vue'
    import Start from './components/Start.vue'
    import Terminal from './components/Terminal.vue'
    import Scoreboard from './components/Scoreboard.vue'

    export default {
        name: 'App',
        components: {
            Header,
            Title,
            Start,
            Terminal,
            Scoreboard
        },
        computed: {
            page_name() {
                return this.$route.name
            }
        }
    }
</script>

<style>

    .text_default {
        font-family: Roboto;
        font-style: normal;
        font-weight: normal;
        font-size: 14px;
        color: #464646;
    }

    .router-link-active {
        font-weight: bold;
    }

</style>
