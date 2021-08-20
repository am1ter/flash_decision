<template>
    <div>
        <div>Decision</div>
    </div>
</template>

<script>
    import { mapState } from 'vuex'
    import { getIterationChart } from '@/api'

    export default {
        name: 'page_Decision',
        computed: {
            ...mapState(['isAuth', 'user', 'currentSession'])
        },
        mounted() {
            console.log('mounted decision page')
            console.log(this.currentSession)
            getIterationChart(this.currentSession.options.sessionId, this.currentSession.iterations.iterationNum)
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
