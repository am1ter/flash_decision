<template>
    <section id='page'>
        <div v-if="apiErrors.length == 0 & isLoaded" class="col-12">
            <b-table outlined striped no-border-collapse hover :items="calcSessionsSummary" :fields="fields" thead-class="d-none" class="shadow">
            </b-table>
            <b-button id="button-go-to-scoreboard" type="submit" class="col-12 gradient rounded-1" :href="scoreboardLink()">Go to the scoreboard</b-button>
        </div>
    </section>
</template>

<script>
    import { mapState } from 'vuex'
    import { apiGetSessionsResults } from '@/api'

    export default {
        name: 'page_Results',
        data() {
            return {
                isLoaded: false,
                fields: [
                    { key: 'column' },
                    { key: 'value', tdClass: 'setValueTdClass' }
                ]
            }
        },
        computed: {
            ...mapState(['user', 'currentSession', 'apiErrors'])
        },
        async mounted() {
            await this.loadSessionsResults()
        },
        methods: {
            async loadSessionsResults() {
                // Load last session results
                let response = await apiGetSessionsResults(this.currentSession.options.sessionId)
                this.currentSession['sessionsResults'] = response
                this.isLoaded = true
            },
            formatFigures(x) {
                return (x > 0) ? '+' + x + '%': x + '%'
            },
            calcSessionsSummary() {
                let sesRes = this.currentSession.sessionsResults
                return [
                    { column: 'Total result', value: this.formatFigures(sesRes.totalResult)},
                    { column: 'Total decisions', value: sesRes.totalDecisions},
                    { column: 'Profitable decisions', value: sesRes.profitableDecisions},
                    { column: 'Unprofitable decisions', value: sesRes.unprofitableDecisions},
                    { column: 'Skipped decisions', value: sesRes.skippedDecisions},
                    { column: 'Median decision’s result', value: this.formatFigures(sesRes.medianDecisionsResult)},
                    { column: 'Best decision’s result', value: this.formatFigures(sesRes.bestDecisionsResult)},
                    { column: 'Worst decision’s result', value: this.formatFigures(sesRes.worstDecisionsResult)},
                    { column: 'Total time spent', value: sesRes.totalTimeSpent},
                ]
            },
            setValueTdClass(value) {
                var firstChar = String(value).charAt(0)
                if(firstChar === '+')
                    return 'text-success'
                else if(firstChar === '-')
                    return 'text-danger'
            },
            scoreboardLink() {
                return '/#/scoreboard' + '/' + this.user.id
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
