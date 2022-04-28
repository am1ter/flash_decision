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
            <ChartCandles :eventBus="eventBus"/>
            <b-button-group class="w-100">
                <b-button id="button-sell" v-on:click="saveDecision($event)" squared variant="danger">Sell ᐁ</b-button>
                <b-button id="button-skip" v-on:click="saveDecision($event)" squared class="ms-1">Skip ᐅ</b-button>
                <b-button id="button-buy" v-on:click="saveDecision($event)" squared variant="success" class="ms-1">Buy ᐃ</b-button>
            </b-button-group>
        </div>
    </section>
</template>

<script>
    import Vue from "vue"
    import { mapState } from "vuex"
    import { apiPostRecordDecision, apiGetIterationInfo } from "@/api"

    // Page subcomponents
    import ChartCandles from "./subcomponents/ChartCandles.vue"

    export default {
        name: "PageDecision",
        components: {
            ChartCandles
        },
        data() {
            return {
                isLoaded: false,
                eventBus: new Vue()
            }
        },
        computed: {
            ...mapState(["user", "currentSession", "apiErrors"])
        },
        async mounted() {
            // Declare hotkeys (listen to keyboard input)
            this.enableHotkeys()
            // If page is reloaded - update vuex objects
            await this.updateObject()
            // Create blank decision when page has been mounted
            await this.createBlankDecision()
            // Show elements
            this.isLoaded = true
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
            async updateObject() {
                // Check if no info for current session found. Page reloaded? Parse url and make api request
                if (Object.keys(this.currentSession["options"]["values"]).length == 0) {
                    this.currentSession["currentIterationNum"] = parseInt(this.$route.params.iteration_num)
                    this.currentSession["iterations"] = {}
                    this.currentSession["decisions"] = {}
                    this.currentSession["decisions"][this.currentSession["currentIterationNum"]] = {"action": null, "timeSpent": null}
                    this.currentSession["options"]["values"] = await apiGetIterationInfo(this.$route.params.session_id, this.currentSession["currentIterationNum"])
                }
            }
            ,
            goNextIteration() {
                // New iteration processing
                // Update vars
                this.currentSession["currentIterationNum"] += 1
                // Change route url
                this.$router.push(`/decision/${this.currentSession["options"]["values"]["sessionId"]}/${this.currentSession["currentIterationNum"]}`)
                // Create blank decision
                this.createBlankDecision()
                // Load new chart
                this.eventBus.$emit('goNextIteration')
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
            padding-bottom: 5px;
        }

</style>
