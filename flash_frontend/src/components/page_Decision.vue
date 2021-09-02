<template>
    <section id="page" v-cloak @keyup.enter="actionBuy">
        <b-alert show variant="success" class="ms-4 me-4 mb-0 p-1 text-center">
            <countdown :end-time="new Date().getTime() + 60000">
                <template v-slot:process="pageTimer">
                    <span>{{ `Time left: ${pageTimer.timeObj.ceil.s}` }} sec. </span>
                </template>
                <template v-slot:finish>
                    <span>The time has ended!</span>
                </template>
            </countdown>
        </b-alert>
        <Plotly :data="iterationChart.data" :layout="layout" :display-mode-bar="false"></Plotly>
        <b-button-group class="ps-4 pe-4 w-100">
            <b-button id="button_sell" v-on:click="actionSell" class="rounded-1" variant="danger">Sell ᐁ</b-button>
            <b-button id="button_skip" v-on:click="actionSkip" class="ms-1 rounded-1">Skip ᐅ</b-button>
            <b-button id="button_buy" v-on:click="actionBuy" class="ms-1 rounded-1" variant="success">Buy ᐃ</b-button>
        </b-button-group>
    </section>
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
            // Declare hotkeys (listen to keyboard input)
            window.addEventListener('keyup', e => {
                (e.key == 'ArrowUp') ? this.actionBuy() :
                (e.key == 'ArrowRight') ? this.actionSkip() :
                (e.key == 'ArrowDown') ? this.actionSell() : null;
                }
            ),
            // Get iteration chart over API
            getIterationChart(this.currentSession.options.sessionId, this.currentSession.currentIterationNum)
                .then(response => {
                    // Chart data to display, iteration data to vuex storage
                    this.iterationChart = JSON.parse(response.data)[0];
                    this.currentSession['iterations']['1'] = JSON.parse(response.data)[1]
                })
        },
        methods: {
            actionSell: () => {
                console.log('sell')
            },
            actionSkip: () => {
                console.log('skip')
            },
            actionBuy: () => {
                console.log('buy')
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
