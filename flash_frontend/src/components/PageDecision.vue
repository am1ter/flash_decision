<template>
    <section id="page" v-if="!isLoading" v-cloak @keyup.enter="actionBuy">
        <div id="bars">
            <countdown 
                ref="pageTimer" 
                :autoStart="false" 
                :left-time="Number(currentSession['options']['values']['timelimit']) * 1000"
                @finish="(vac) => saveDecision(vac)">
                <template v-slot:process="pageTimer">
                    <b-progress class="squared" height="12px" :max="pageTimer.leftTime / 1000">
                        <b-progress-bar :value="(pageTimer.leftTime - pageTimer.remainingTime) / 1000" variant="success" striped :animated="true"/>
                        <b-progress-bar id= "bar-time-left" :value="pageTimer.remainingTime / 1000" variant="secondary" :class="{'bg-danger': pageTimer.timeObj.ceil.s <= 3}" >
                            {{pageTimer.timeObj.ceil.s + ' s.'}}
                        </b-progress-bar>
                    </b-progress>
                </template>
                <template v-slot:finish>
                    <b-progress class="squared" height="12px" :value="100" :max="100" variant="success"/>
                </template>
            </countdown>
            <ChartCandles :iterationChart="iterationChart"/>
            <b-progress class="squared mb-2" height="7px" :max="currentSession['options']['values']['iterations']">
                <b-progress-bar :value="currentSession['currentIterationNum'] - 1" variant="dark"/>
                <b-progress-bar :value="1" variant="success"/>
                <b-progress-bar :value="currentSession['options']['values']['iterations'] - currentSession['currentIterationNum']" variant="secondary"/>
            </b-progress>
            <b-button-group class="w-100">
                <b-button id="button-sell" v-on:click="saveDecision($event)" squared variant="danger">Sell ᐁ</b-button>
                <b-button id="button-skip" v-on:click="saveDecision($event)" squared class="ms-1">Skip ᐅ</b-button>
                <b-button id="button-buy" v-on:click="saveDecision($event)" squared variant="success" class="ms-1">Buy ᐃ</b-button>
            </b-button-group>
        </div>
    </section>
</template>

<script>
    import { mapState, mapMutations, mapGetters } from "vuex"
    import { apiRecordDecision, apiRenderChart } from "@/api"

    // Page subcomponents
    import ChartCandles from "./subcomponents/ChartCandles.vue"

    export default {
        name: "PageDecision",
        components: {
            ChartCandles
        },
        data() {
            return {
                iterationChart: {}
            }
        },
        computed: {
            ...mapState(["user", "currentSession", "isLoading"]),
            ...mapGetters(["sessionMode"])
        },
        async beforeMount() {
            // Start page loading
            this.startLoading()
            // Declare hotkeys (listen to keyboard input)
            this.enableHotkeys()
            // Create blank decision when page has been mounted
            this.createBlankDecision()
            // If page is reloaded - update vuex objects
            await this.updateIfPageRefresh()
            // Load new chart
            await this.createChart()
            // Display page
            await this.stopLoading()
            // Start countdown
            this.startCountdown()
        },
        async beforeRouteUpdate(to, from, next) {
            // Start page loading after route updating
            this.startLoading()
            // Create blank decision
            this.createBlankDecision()
            // Load new chart if requested iteration exists
            if (await this.createChart()) {
                await this.stopLoading()
            }
            // Restart countdown
            next()
            this.startCountdown()
        },
        methods: {
            ...mapMutations(["startLoading", "stopLoading", "newApiError"]),
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
            async updateIfPageRefresh() {
                // Check if no info for current session found. Page reloaded? Parse url and make api request
                if (Object.keys(this.currentSession["options"]["values"]).length == 0) {
                    this.currentSession["currentIterationNum"] = parseInt(this.$route.params.iteration_num)
                    this.currentSession["mode"] = this.$route.params.mode
                    this.currentSession["iterations"] = {}
                    this.currentSession["decisions"] = {}
                    this.currentSession["decisions"][this.currentSession["currentIterationNum"]] = {"action": null, "timeSpent": null}

                    // Wait for async methods
                    let response = (await apiRenderChart(this.sessionMode, this.$route.params.session_id, this.currentSession["currentIterationNum"])).data
                    // Check response
                    if (response["isIterationFound"] == false) {
                        this.newApiError("Iteration not found. Please start new session.")
                    }
                    // Add attributes from response to the object
                    this.currentSession["options"]["values"]["sessionId"] = response["values"]["SessionId"]
                    this.currentSession["options"]["values"]["timelimit"] = response["values"]["Timelimit"]
                    this.currentSession["options"]["values"]["iterations"] = response["values"]["Iterations"]
                    this.currentSession["options"]["values"]["barsnumber"] = response["values"]["Barsnumber"]
                    this.currentSession["options"]["values"]["fixingbar"] = response["values"]["Fixingbar"]
                    this.currentSession["options"]["values"]["slippage"] = response["values"]["Slippage"]

                    this.currentSession["options"]["aliases"] = {
                        "market": response.aliases["Market"],
                        "ticker": response.aliases["Ticker"],
                        "timeframe": response.aliases["Timeframe"],
                        "barsnumber": response.aliases["Barsnumber"],
                        "timelimit": response.aliases["Timelimit"],
                        "date": response.aliases["Date"],
                        "iterations": response.aliases["Iterations"],
                        "slippage": response.aliases["Slippage"],
                        "fixingbar": response.aliases["Fixingbar"]
                    }

                }
            },
            async createChart() {
                // Run async request - пet iteration chart over API
                let response = (await apiRenderChart(this.sessionMode, this.$route.params.session_id, this.currentSession["currentIterationNum"])).data
                let status = false

                // Use response to draw chart and save values to vuex object
                if (response['isIterationFound']) {
                    this.iterationChart = JSON.parse(response["chart"]);
                    this.currentSession["iterations"][this.currentSession["currentIterationNum"]] = response["values"]
                    status = true
                } else {
                    // If response is `false` then skip decision for such iteration 
                    this.iterationChart = {}
                    this.currentSession["iterations"][this.currentSession["currentIterationNum"]] = this.currentSession["iterations"][this.currentSession["currentIterationNum"] - 1]
                    let event = {"target": {"id": "button-skip"}}
                    await this.saveDecision(event)
                }
                return status
            },
            async saveDecision(event) {
                // Decision has been made

                let action = null;

                // Check that current iteration is okay
                if (this.currentSession["decisions"].length < this.currentSession["currentIterationNum"]) {
                    return false
                }

                // Only 1 decision is possible - stop if decision is already saved to vuex
                if (this.currentSession["decisions"][this.currentSession["currentIterationNum"]]["action"] != null) {
                    return false
                }

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
                this.currentSession["decisions"][this.currentSession["currentIterationNum"]]["timeSpent"] = this.$refs.pageTimer.runTimes

                // Get the time spent from the Countdown component and finish countdown
                if (!this.isLoading) {
                    this.$refs.pageTimer.finishCountdown()
                }

                // Send post request
                await apiRecordDecision(this.sessionMode, this.$route.params.session_id, this.currentSession["currentIterationNum"], this.currentSession["decisions"][this.currentSession["currentIterationNum"]])
                // When post request has been processed go to the next iteration or to the results page
                if (this.currentSession["currentIterationNum"] < Number(this.currentSession["options"]["values"]["iterations"])) {
                    await this.goNextIteration()
                } else {
                    this.$router.push(`/sessions-results/${this.currentSession["mode"]}/${this.currentSession["options"]["values"]["sessionId"]}`)
                }
            },
            goNextIteration() {
                // New iteration processing
                // Update vars
                this.currentSession["currentIterationNum"] += 1
                // Change route url
                this.$router.push(`/sessions/${this.sessionMode}/${this.currentSession["options"]["values"]["sessionId"]}/iterations/${this.currentSession["currentIterationNum"]}`)
            },
            startCountdown() {
                // Start or restart countdown
                if (!this.isLoading) {
                    this.$refs.pageTimer.startCountdown(true)
                }
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

    #bars {
            max-width: 453px;
            width: 100%;
            padding-bottom: 5px;
        }

    .squared {
        border-radius: 0px;
        font-size: 0.55rem;
    }

    #bar-time-left {
        padding-left: 3px;
        text-align: left;
    }

</style>
