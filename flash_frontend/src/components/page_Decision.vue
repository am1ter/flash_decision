<template>
    <section id="page" v-cloak @keyup.enter="actionBuy">
        <div id='errors' v-if="apiErrors.length > 0">
            <p>{{apiErrors[0]}}</p>
        </div>
        <div id='content' v-if="apiErrors == 0">
            <b-alert show variant="success" class="ms-4 me-4 mb-0 p-1 text-center">
                <countdown 
                    ref="pageTimer" 
                    :autoStart="false" 
                    :left-time="Number(currentSession.options.timelimit) * 1000"
                    @finish="(vac) => saveDecision(vac)">
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
                <b-button id="button_sell" v-on:click="saveDecision($event)" class="rounded-1" variant="danger">Sell ᐁ</b-button>
                <b-button id="button_skip" v-on:click="saveDecision($event)" class="ms-1 rounded-1">Skip ᐅ</b-button>
                <b-button id="button_buy" v-on:click="saveDecision($event)" class="ms-1 rounded-1" variant="success">Buy ᐃ</b-button>
            </b-button-group>
        </div>
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
                // Current iteration chart data
                temp: 15000,
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
                },
                apiErrors: []
            }
        },
        computed: {
            ...mapState(['isAuth', 'user', 'currentSession'])
        },
        mounted() {
            // Declare hotkeys (listen to keyboard input)
            window.addEventListener('keyup', event => {
                    if (event.key == 'ArrowDown' || event.key == 'ArrowRight' || event.key == 'ArrowUp' ) {
                        this.saveDecision(event)
                    } 
                }
            ),
            // Create blank decision when page has been mounted
            this.createBlankDecision()
            // Load first chart
            this.updateChart()
            // Start countdown
            this.$refs.pageTimer.startCountdown()
        },
        methods: {
            // Create blank decision
            createBlankDecision() {
                if (this.currentSession.currentIterationNum == 1) {
                    this.currentSession['decisions'] = {1: {'action': null, 'timeSpent': null}}}
                else {
                    this.currentSession['decisions'][this.currentSession.currentIterationNum] = {'action': null, 'timeSpent': null}
                }
            },
            updateChart() {
            // Get iteration chart over API
            return getIterationChart(this.currentSession.options.sessionId, this.currentSession.currentIterationNum)
                    .then(response => {
                        // Check that all iterations exists
                        try {
                            // Chart data to display [0], iteration data to vuex storage [1]
                            this.iterationChart = JSON.parse(response.data)[0];
                            this.currentSession['iterations'][this.currentSession.currentIterationNum] = JSON.parse(response.data)[1]
                        }
                        catch (error) {
                            this.apiErrors.push(error)
                        }
                    },
                    reject => {this.apiErrors.push(reject)}
                    )
            },
            // Decision has been made
            saveDecision(event) {

                // Check that current iteration is okay
                if (this.currentSession['decisions'].length < this.currentSession.currentIterationNum) {
                    return false
                }

                // Only 1 decision is possible - stop if decision is already saved to vuex
                if (this.currentSession['decisions'][this.currentSession.currentIterationNum]['action'] != null) {
                    return false
                }

                // Get the time spent from the Countdown component
                let timeSpent = this.$refs.pageTimer.runTimes;
                let action = null;

                // Get an action type from timer, button or hotkey
                if (event.timeObj) {
                    action = 'Skip'
                } else if (event.target.id) {
                    action = 
                        (event.target.id == 'button_sell') ? 'Sell' :
                        (event.target.id == 'button_skip') ? 'Skip' :
                        (event.target.id == 'button_buy') ? 'Buy' : null;
                } else if (event.key) {
                    action = 
                        (event.key == 'ArrowDown') ? 'Sell' :
                        (event.key == 'ArrowRight') ? 'Skip' :
                        (event.key == 'ArrowUp') ? 'Buy' : null;
                }

                // Save decision to the vuex object
                this.currentSession['decisions'][this.currentSession.currentIterationNum]['action'] = action
                this.currentSession['decisions'][this.currentSession.currentIterationNum]['timeSpent'] = timeSpent

                // Finish countdown
                this.$refs.pageTimer.finishCountdown()

                // Send post request
                // TODO

                // Go to the next iteration
                if (this.currentSession.currentIterationNum < Number(this.currentSession.options.iterations)) {
                    this.goNextIteration()
                } else {
                    this.$router.push('/scoreboard/' + this.currentSession.options.sessionId)
                }
            },
            goNextIteration() {
                // New iteration processing
                // Update vars
                this.currentSession.currentIterationNum += 1
                // Change route url
                this.$router.push('/decision/' + this.currentSession.options.sessionId + '/' + this.currentSession.currentIterationNum)
                // Create blank decision
                this.createBlankDecision()
                // Load new chart
                this.updateChart()
                // Restart countdown
                this.$refs.pageTimer.startCountdown(true)
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
