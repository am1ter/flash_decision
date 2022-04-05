<template>
    <section id="page" v-cloak @keyup.enter="actionBuy">
        <div id='bars' v-if="apiErrors.length == 0">
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
                <b-button id="button-sell" v-on:click="saveDecision($event)" class="rounded-1" variant="danger">Sell ᐁ</b-button>
                <b-button id="button-skip" v-on:click="saveDecision($event)" class="ms-1 rounded-1">Skip ᐅ</b-button>
                <b-button id="button-buy" v-on:click="saveDecision($event)" class="ms-1 rounded-1" variant="success">Buy ᐃ</b-button>
            </b-button-group>
        </div>
    </section>
</template>

<script>
    import { mapState } from 'vuex'
    import { Plotly } from 'vue-plotly'
    import { apiGetIterationChart, apiPostRecordDecision } from '@/api'

    export default {
        name: 'page_Decision',
        components: {
            Plotly
        },
        data() {
            return {
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
            ...mapState(['user', 'currentSession', 'apiErrors'])
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
            createBlankDecision() {
                // Create blank decision
                if (this.currentSession.currentIterationNum == 1) {
                    this.currentSession['decisions'] = {1: {'action': null, 'timeSpent': null}}}
                else {
                    this.currentSession['decisions'][this.currentSession.currentIterationNum] = {'action': null, 'timeSpent': null}
                }
            },
            async updateChart() {
                // Get iteration chart over API
                let response = await apiGetIterationChart(this.currentSession.options.sessionId, this.currentSession.currentIterationNum)
                // Chart data to display [0], iteration data to vuex storage [1]
                if (response) {
                    this.iterationChart = JSON.parse(response)[0];
                    this.currentSession['iterations'][this.currentSession.currentIterationNum] = JSON.parse(response)[1]
                } else {
                    // If response is `false` then skip decision for such iteration 
                    this.iterationChart = JSON.parse(false);
                    this.currentSession['iterations'][this.currentSession.currentIterationNum] = this.currentSession['iterations'][this.currentSession.currentIterationNum - 1]
                    document.getElementById("button-skip").click(); 
                }
            },
            async saveDecision(event) {
                // Decision has been made

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
                        (event.target.id == 'button-sell') ? 'Sell' :
                        (event.target.id == 'button-skip') ? 'Skip' :
                        (event.target.id == 'button-buy') ? 'Buy' : null;
                } else if (event.key) {
                    action = 
                        (event.key == 'ArrowDown') ? 'Sell' :
                        (event.key == 'ArrowRight') ? 'Skip' :
                        (event.key == 'ArrowUp') ? 'Buy' : null;
                }

                // Save decision to the vuex object
                this.currentSession['decisions'][this.currentSession.currentIterationNum]['sessionId'] = this.currentSession.options.sessionId
                this.currentSession['decisions'][this.currentSession.currentIterationNum]['iterationNum'] = this.currentSession.currentIterationNum
                this.currentSession['decisions'][this.currentSession.currentIterationNum]['action'] = action
                this.currentSession['decisions'][this.currentSession.currentIterationNum]['timeSpent'] = timeSpent

                // Finish countdown
                this.$refs.pageTimer.finishCountdown()

                // Send post request
                await apiPostRecordDecision(this.currentSession['decisions'][this.currentSession.currentIterationNum])
                // When post request has been processed go to the next iteration or to the results page
                if (this.currentSession.currentIterationNum < Number(this.currentSession.options.iterations)) {
                    this.goNextIteration()
                } else {
                    this.$router.push('/sessions-results/' + this.currentSession.options.sessionId)
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

#bars {
        width: 453px;
        padding-bottom: 15px;
    }

</style>
