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
        data() {
            return {
                iterationChart: {}
            }
        },
        computed: {
            ...mapState(['isAuth', 'user', 'currentSession'])
        },
        mounted() {
            console.log('mounted decision page')
            console.log(this.currentSession)
            getIterationChart(this.currentSession.options.sessionId, this.currentSession.iterations.iterationNum)
                .then(response => {
                    this.iterationChart = response.data
                })
            console.log(this.iterationChart)
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
