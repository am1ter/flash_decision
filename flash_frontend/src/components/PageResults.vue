<template>
    <section id="page" v-if="apiErrors.length == 0 & !isLoading">
        <div class="col-12">
            <b-table outlined striped no-border-collapse hover :items="calcSessionsSummary" :fields="fields" thead-class="d-none" class="shadow">
            </b-table>
            <b-button id="button-go-to-scoreboard" type="submit" squared class="col-12 gradient"
                href="#" v-on:click="$router.push(`/scoreboard/${currentSession['options']['values']['mode']}/${user.id}/`)">
                Go to the scoreboard
            </b-button>
            <b-button id="button-start-new-session" type="submit" squared variant="outline-secondary" class="col-12 mt-2" 
                href="#" v-on:click="$router.push(`/session/`)">
                Start new session
            </b-button>
        </div>
    </section>
</template>

<script>
    import { mapState, mapMutations } from "vuex"
    import { apiGetSessionsResults } from "@/api"

    export default {
        name: "PageResults",
        data() {
            return {
                fields: [
                    { key: "column" },
                    { key: "value", tdClass: this.formatFiguresColor }
                ]
            }
        },
        computed: {
            ...mapState(["user", "currentSession", "apiErrors", "isLoading"])
        },
        async beforeMount() {
            // Start page loading
            this.startLoading()
            // Load last session results
            await this.loadSessionsResults()
            // Display page
            this.stopLoading()
        },
        methods: {
            ...mapMutations(["startLoading", "stopLoading"]),
            async loadSessionsResults() {
                // Load last session results
                // Check if no info for current session found. Page reloaded? Parse url and make api request
                if (Object.keys(this.currentSession["options"]["values"]).length == 0) {
                    this.currentSession["options"]["values"]["sessionId"] = parseInt(this.$route.params.session_id)
                }
                let response = await apiGetSessionsResults(this.currentSession["options"]["values"]["sessionId"])
                this.currentSession["sessionsResults"] = response
            },
            formatFigures(x) {
                // Improve text display of figures
                return (x > 0) ? "+" + x + "%": x + "%"
            },
            calcSessionsSummary() {
                let sesRes = this.currentSession.sessionsResults
                return [
                    { column: "Total result", value: this.formatFigures(sesRes.totalResult)},
                    { column: "Total decisions", value: sesRes.totalDecisions},
                    { column: "Profitable decisions", value: sesRes.profitableDecisions},
                    { column: "Unprofitable decisions", value: sesRes.unprofitableDecisions},
                    { column: "Skipped decisions", value: sesRes.skippedDecisions},
                    { column: "Median decision’s result", value: this.formatFigures(sesRes.medianDecisionsResult)},
                    { column: "Best decision’s result", value: this.formatFigures(sesRes.bestDecisionsResult)},
                    { column: "Worst decision’s result", value: this.formatFigures(sesRes.worstDecisionsResult)},
                    { column: "Total time spent", value: sesRes.totalTimeSpent}
                ]
            },
            formatFiguresColor(value) {
                let firstChar = String(value).charAt(0)
                if(firstChar === "+")
                    return "text-success"
                else if(firstChar === "-")
                    return "text-danger"
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
