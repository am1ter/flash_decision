<template>
    <section id="page" v-if="apiErrors.length == 0 & isLoaded" v-cloak @keyup.enter="actionBuy">
        <div id="bars">
            <b-alert show variant="success" class="mb-0 p-1 text-center">
                <countdown 
                    ref="pageTimer" 
                    :autoStart="true" 
                    :left-time="Number(currentSession['options']['values']['timelimit']) * 1000"
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
            <b-button-group class="w-100">
                <b-button id="button-sell" v-on:click="saveDecision($event)" squared variant="danger">Sell ᐁ</b-button>
                <b-button id="button-skip" v-on:click="saveDecision($event)" squared class="ms-1">Skip ᐅ</b-button>
                <b-button id="button-buy" v-on:click="saveDecision($event)" squared variant="success" class="ms-1">Buy ᐃ</b-button>
            </b-button-group>
        </div>
    </section>
</template>

<script>
    import { mapState } from "vuex"
    import { Plotly } from "vue-plotly"
    import { apiGetIterationChart, apiGetIterationInfo, apiPostRecordDecision } from "@/api"

    export default {
        name: "PageDecision",
        components: {
            Plotly
        },
        data() {
            return {
                isLoaded: false,
                iterationChart: {},
                // Chart layout properties
                layout: {
                    title: {visible: false},
                    dragmode: "zoom",
                    showlegend: false,
                    height: 350,
                    margin: {
                        r: 0,
                        t: 25,
                        b: 25,
                        l: 0
                    },
                    xaxis: {
                        autorange: true,
                        rangeslider: {visible: false},
                        title: {visible: false},
                        showticklabels: false
                        },
                    annotations: [
                        {
                        x: 0,
                        y: 0.5,
                        xref: 'x',
                        yref: 'paper',
                        text: 'Your<br>decision?',
                        font: {color: 'black'},
                        showarrow: true,
                        xanchor: 'right',
                        ax: 0,
                        ay: 0
                        }
                    ],
                    shapes: [
                        {
                        type: 'rect',
                        xref: 'x',
                        yref: 'paper',
                        x0: 0,
                        y0: 0,
                        x1: 0,
                        y1: 1,
                        fillcolor: '#d3d3d3',
                        opacity: 0.2,
                        line: {
                            width: 0
                        }
                        },
                        {
                        type: 'rect',
                        xref: 'x',
                        yref: 'paper',
                        x0: 0,
                        y0: 0,
                        x1: 0,
                        y1: 1,
                        fillcolor: '#d3d3d3',
                        opacity: 0.5,
                        line: {
                            width: 0
                        }
                        },
                        {
                        type: 'rect',
                        xref: 'x',
                        yref: 'paper',
                        x0: 0,
                        y0: 0,
                        x1: 0,
                        y1: 1,
                        fillcolor: '#d3d3d3',
                        opacity: 0.5,
                        line: {
                            width: 0
                        }
                        }
                        ]
                }
            }
        },
        computed: {
            ...mapState(["user", "currentSession", "apiErrors"])
        },
        mounted() {
            // Declare hotkeys (listen to keyboard input)
            this.enableHotkeys()
            // Create blank decision when page has been mounted
            this.createBlankDecision()
            // Load first chart
            this.updateChart()
        },
        methods: {
            enableHotkeys() {
                window.addEventListener("keyup", event => {
                if (event.key == "ArrowDown" || event.key == "ArrowRight" || event.key == "ArrowUp" ) {
                    this.saveDecision(event)}
                }
                )
            },
            async createBlankDecision() {
                // Create blank decision
                if (this.currentSession["currentIterationNum"] == 1) {
                    // First iteration
                    this.currentSession["decisions"] = {1: {"action": null, "timeSpent": null}}}
                else if (this.currentSession["currentIterationNum"] > 1) {
                    // Following iterations
                    this.currentSession["decisions"][this.currentSession["currentIterationNum"]] = {"action": null, "timeSpent": null}
                }
            },
            async updateChart() {
                // Check if no info for current session found. Page reloaded? Parse url and make api request
                if (Object.keys(this.currentSession["options"]["values"]).length == 0) {
                    this.currentSession["currentIterationNum"] = parseInt(this.$route.params.iteration_num)
                    this.currentSession["iterations"] = {}
                    this.currentSession["decisions"] = {}
                    this.currentSession["decisions"][this.currentSession["currentIterationNum"]] = {"action": null, "timeSpent": null}
                    this.currentSession["options"]["values"] = await apiGetIterationInfo(this.$route.params.session_id, this.currentSession["currentIterationNum"])
                }
                // Get iteration chart over API
                let response = await apiGetIterationChart(this.currentSession["options"]["values"]["sessionId"], this.currentSession["currentIterationNum"])
                // Chart data to display [0], iteration data to vuex storage [1]
                if (response) {
                    this.iterationChart = JSON.parse(response)[0];
                    this.currentSession["iterations"][this.currentSession["currentIterationNum"]] = JSON.parse(response)[1]
                } else {
                    // If response is `false` then skip decision for such iteration 
                    this.iterationChart = JSON.parse(false);
                    this.currentSession["iterations"][this.currentSession["currentIterationNum"]] = this.currentSession["iterations"][this.currentSession["currentIterationNum"] - 1]
                    document.getElementById("button-skip").click(); 
                }
                // Format chart - add extra space to the graph
                let finalbar = parseInt(this.currentSession["options"]["values"]["barsnumber"])
                let fixingbar = parseInt(this.currentSession["options"]["values"]["fixingbar"])
                this.layout.annotations[0].ax = fixingbar * -1
                this.layout.annotations[0].x = finalbar + fixingbar
                this.layout.shapes[0].x0 = finalbar
                this.layout.shapes[0].x1 = finalbar + fixingbar
                this.layout.shapes[1].x0 = finalbar
                this.layout.shapes[1].x1 = finalbar + 1
                this.layout.shapes[2].x0 = finalbar + fixingbar - 1
                this.layout.shapes[2].x1 = finalbar + fixingbar
                // Show elements
                this.isLoaded = true
            },
            async saveDecision(event) {
                // Decision has been made

                // Check that current iteration is okay
                if (this.currentSession["decisions"].length < this.currentSession["currentIterationNum"]) {
                    return false
                }

                // Only 1 decision is possible - stop if decision is already saved to vuex
                if (this.currentSession["decisions"][this.currentSession["currentIterationNum"]]["action"] != null) {
                    return false
                }

                // Get the time spent from the Countdown component
                let timeSpent = this.$refs.pageTimer.runTimes;
                let action = null;

                // Get an action type from timer, button or hotkey
                if (event.timeObj) {
                    action = "Skip"
                } else if (event.target.id) {
                    action = 
                        (event.target.id == "button-sell") ? "Sell" :
                        (event.target.id == "button-skip") ? "Skip" :
                        (event.target.id == "button-buy") ? "Buy" : null;
                } else if (event.key) {
                    action = 
                        (event.key == "ArrowDown") ? "Sell" :
                        (event.key == "ArrowRight") ? "Skip" :
                        (event.key == "ArrowUp") ? "Buy" : null;
                }

                // Save decision to the vuex object
                this.currentSession["decisions"][this.currentSession["currentIterationNum"]]["sessionId"] = this.currentSession["options"]["values"]["sessionId"]
                this.currentSession["decisions"][this.currentSession["currentIterationNum"]]["iterationNum"] = this.currentSession["currentIterationNum"]
                this.currentSession["decisions"][this.currentSession["currentIterationNum"]]["action"] = action
                this.currentSession["decisions"][this.currentSession["currentIterationNum"]]["timeSpent"] = timeSpent

                // Finish countdown
                this.$refs.pageTimer.finishCountdown()

                // Send post request
                await apiPostRecordDecision(this.currentSession["decisions"][this.currentSession["currentIterationNum"]])
                // When post request has been processed go to the next iteration or to the results page
                if (this.currentSession["currentIterationNum"] < Number(this.currentSession["options"]["values"]["iterations"])) {
                    this.goNextIteration()
                } else {
                    this.$router.push(`/sessions-results/${this.currentSession["options"]["values"]["sessionId"]}`)
                }
            },
            goNextIteration() {
                // New iteration processing
                // Update vars
                this.currentSession["currentIterationNum"] += 1
                // Change route url
                this.$router.push(`/decision/${this.currentSession["options"]["values"]["sessionId"]}/${this.currentSession["currentIterationNum"]}`)
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
        max-width: 453px;
        width: 100%;
        padding-bottom: 15px;
    }

</style>
