<template>
    <div>
        <Plotly :data="iterationChart.data" :layout="layout" :display-mode-bar="false"></Plotly>
        <b-button-group class="ps-3 pe-3 w-100">
            <b-button class="rounded-1" variant="danger">Sell ᐁ</b-button>
            <b-button class="ms-1 rounded-1">Skip ᐅ</b-button>
            <b-button class="ms-1 rounded-1" variant="success">Buy ᐃ</b-button>
        </b-button-group>
    </div>
</template>

<script>
    import { mapState } from 'vuex'
    import { Plotly } from 'vue-plotly'
    import { getIterationChart } from '@/api'

    export default {
        name: 'page_Decision',
        components: {
            Plotly
        },
        data() {
            return {
                // TODO: Delete before release
                // currentSession: {'options': {'sessionId': 63},
                //             'iterations': {'iterationNum': 1}
                // },
                iterationChart: {},
                // Chart layout properties
                layout: {
                    title: {visible: false},
                    dragmode: 'zoom',
                    showlegend: false,
                    height: 350,
                    margin: {
                        r: 25,
                        t: 25,
                        b: 25,
                        l: 60
                    },
                    xaxis: {
                        autorange: true,
                        rangeslider: {visible: false},
                        title: {visible: false},
                        showticklabels: false
                        }
                }
            }
        },
        computed: {
            ...mapState(['isAuth', 'user', 'currentSession'])
        },
        mounted() {
            getIterationChart(this.currentSession.options.sessionId, this.currentSession.currentIterationNum)
                .then(response => {
                    // Chart data to display, iteration data to vuex storage
                    this.iterationChart = JSON.parse(response.data)[0];
                    this.currentSession['iterations']['1'] = JSON.parse(response.data)[1]
                })
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
